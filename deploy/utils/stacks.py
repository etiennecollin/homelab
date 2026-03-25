import json
from dataclasses import dataclass, field
from pathlib import Path
from shlex import quote
from textwrap import dedent
from typing import Any, Callable, Optional, cast

from pyinfra.context import host
from pyinfra.facts.server import Command
from pyinfra.operations import files, server

from .types import Directory, FileCopy
from .utils import dget, remote_path

BASE_DIR = Path(__file__).resolve().parents[2]
STACKS_DIR = BASE_DIR / "stacks"
TEMPLATES_DIR = BASE_DIR / "deploy" / "templates"


@dataclass
class StackBase:
    """
    Immutable definition of a stack.

    This class represents the *base layer* of a stack, which is intended to be
    version-controlled and shared across environments. It contains everything
    required to deploy the stack except for user-specific configuration.

    Responsibilities:
    - Define filesystem structure (directories)
    - Define static files to copy
    - Define Jinja2 templates to render
    - Optionally define a post-deployment hook

    This class MUST NOT contain any sensitive data or environment-specific values.
    """

    name: str
    """
    Name of the stack, should match the name of the stack directory in `./stacks`
    """

    directories: list[Directory] = field(default_factory=list)
    """
    List of directories that must exist on the remote host prior to deployment.
    These are created with controlled permissions.
    """

    static_files: list[FileCopy] = field(default_factory=list)
    """
    Files copied as-is to the remote host. These may optionally be empty files
    if `src` is None.
    """

    template_files: list[FileCopy] = field(default_factory=list)
    """
    Files rendered using Jinja2. The rendering context is composed of:
    - shared environment variables
    - stack-specific environment variables
    - stack-specific template variables
    """

    post_deploy: Optional[Callable[["Stack"], None]] = None
    """
    Optional callback executed after all files are deployed. This can be used
    for additional pyinfra operations that are not covered by the standard flow.
    Receives the instantiated `Stack` as its only argument.
    """


@dataclass
class StackConfig:
    """
    User-defined configuration for a stack.

    This class represents the configuration layer of a stack, typically stored
    in encrypted files. It contains environment-specific and sensitive values.

    Responsibilities:
    - Enable/disable the stack
    - Provide environment variables for docker-compose
    - Provide variables used in Jinja2 templates
    """

    enabled: bool = True
    """
     Whether this stack should be deployed. Disabled stacks are ignored
    during deployment.
    """

    env: dict[str, str] = field(default_factory=dict)
    """
    Environment variables injected into:
    - the generated `stack.env` file
    - the docker-compose runtime (`--env-file`)
    These override shared environment variables when keys overlap.
    """

    template_vars: dict[str, Any] = field(default_factory=dict)
    """
    Arbitrary variables passed to Jinja2 templates. These take highest
    precedence in the rendering context and can override values from `env`
    or shared variables if necessary.
    """


@dataclass
class Stack:
    """
    Fully instantiated stack combining base definition and user configuration.

    This class is the runtime representation of a stack. It merges the immutable
    `StackBase` with a `StackConfig` and provides deployment lifecycle operations.

    Responsibilities:
    - Materialize filesystem structure on the remote host
    - Render configuration files and templates
    - Manage docker-compose lifecycle (deploy, start, teardown)

    The deployment process is split into phases:
    - deploy(): filesystem + configuration rendering
    - start(): docker-compose validation, pull, and up
    - teardown(): conditional shutdown of running stacks
    """

    base: StackBase
    """The base stack definition (shared, non-sensitive)."""

    config: StackConfig = field(default_factory=StackConfig)
    """The user-provided configuration (environment-specific, possibly sensitive)."""

    @property
    def name(self) -> str:
        """
        Returns the stack name.

        This is a convenience proxy to `StackBase.name`.
        """
        return self.base.name

    @property
    def enabled(self) -> bool:
        """
        Indicates whether this stack is enabled.

        This is a convenience proxy to `StackConfig.enabled`.
        """
        return self.config.enabled

    def deploy(self):
        """
        Prepare the stack on the remote host.

        This method is responsible for all filesystem and configuration steps:
        - Create the root stack directory
        - Create declared subdirectories
        - Upload the docker-compose file
        - Upload static files
        - Render and upload `stack.env`
        - Render and upload template files
        - Execute optional post-deploy hook

        Notes:
        - All operations are performed with controlled ownership and permissions.
        - Template rendering context is merged as:
            - shared_env < config.env < config.template_vars
        - Docker containers are NOT started here. Use `start()` for that.
        """

        # Directories
        local_stack_dir = STACKS_DIR / self.name
        remote_stack_dir = remote_path(self.name)

        # Environment
        shared_env = dget("env", {}) or {}

        # -------------------------
        # Ensure directory
        # -------------------------
        files.directory(
            name=f"[{self.name}] create stack directory",
            path=str(remote_stack_dir),
            mode="755",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
        )

        # -------------------------
        # Deploy directories
        # -------------------------
        for dir in self.base.directories:
            files.directory(
                name=f"[{self.name}] create directory {dir.path}",
                path=str(dir.resolve_path(remote_stack_dir)),
                mode=dir.mode,
                user=dget("docker_user"),
                group=dget("docker_group"),
                _sudo=True,
            )

        # -------------------------
        # Deploy compose.yaml
        # -------------------------
        files.put(
            name=f"[{self.name}] deploy compose.yaml",
            src=str(local_stack_dir / "compose.yaml"),
            dest=str(remote_stack_dir / "compose.yaml"),
            mode="644",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
        )

        # -------------------------
        # Deploy static files
        # -------------------------
        for file in self.base.static_files:
            dest = str(file.resolve_dest(remote_stack_dir))

            if file.src is not None:
                files.put(
                    name=f"[{self.name}] deploy {file.dest}",
                    src=str(file.resolve_src(local_stack_dir)) if isinstance(file.src, Path) else file.src,
                    dest=dest,
                    mode=file.mode,
                    create_remote_dir=False,  # Enforce usage of self.base.directories
                    user=dget("docker_user"),
                    group=dget("docker_group"),
                    _sudo=True,
                )
            else:
                files.file(
                    name=f"[{self.name}] create file {file.dest}",
                    path=dest,
                    mode=file.mode,
                    create_remote_dir=False,  # Enforce usage of self.base.directories
                    user=dget("docker_user"),
                    group=dget("docker_group"),
                    _sudo=True,
                )

        # -------------------------
        # Deploy stack.env
        # -------------------------
        files.template(
            name=f"[{self.name}] deploy stack.env",
            src=str(TEMPLATES_DIR / "stack.env.j2"),
            dest=str(remote_stack_dir / "stack.env"),
            mode="600",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
            shared_env=shared_env,
            stack_env=self.config.env,
        )

        # -------------------------
        # Deploy templates
        # -------------------------
        template_context = {
            **shared_env,  # shared
            **self.config.env,  # config
            **self.config.template_vars,  # template
        }

        for file in self.base.template_files:
            assert file.src is not None, "Template files require a source path"
            files.template(
                name=f"[{self.name}] deploy {file.dest}",
                src=str(file.resolve_src(local_stack_dir)) if isinstance(file.src, Path) else file.src,
                dest=str(file.resolve_dest(remote_stack_dir)),
                mode=file.mode,
                create_remote_dir=False,  # Enforce usage of self.base.directories
                user=dget("docker_user"),
                group=dget("docker_group"),
                _sudo=True,
                **cast(dict[str, Any], template_context),
            )

        # -------------------------
        # Post-deploy hook
        # -------------------------
        if self.base.post_deploy:
            self.base.post_deploy(self)

    def start(self):
        """
        Start or update the stack using docker-compose.

        This method performs:
        - Validation of the compose configuration
        - Pulling of container images
        - Deployment via `docker compose up`

        Behavior:
        - Uses `stack.env` for environment injection
        - Forces recreation of containers to ensure consistency

        Notes:
        - No action is taken if `dry_run` is enabled
        - Assumes `deploy()` has already been executed
        """
        if dget("dry_run", False):
            return

        remote_stack_dir = remote_path(self.name)
        sudo_docker = dget("docker_use_sudo", True)

        # -------------------------
        # Validate
        # -------------------------
        server.shell(
            name=f"[{self.name}] validate compose",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env config > /dev/null
                """).strip()],
            _sudo=sudo_docker,
        )

        # -------------------------
        # Pull
        # -------------------------
        server.shell(
            name=f"[{self.name}] pull images",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env pull
                """).strip()],
            _sudo=sudo_docker,
        )

        # -------------------------
        # Up
        # -------------------------
        server.shell(
            name=f"[{self.name}] deploy stack",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env up -d --remove-orphans --force-recreate
                """).strip()],
            _sudo=sudo_docker,
        )

    def teardown(self):
        """
        Stop the stack if it is currently running.

        This method:
        - Queries docker for active compose stacks
        - Checks if this stack is running and matches the expected path
        - Executes `docker compose down` if needed

        Behavior:
        - No-op if the stack is not running
        - Uses `--remove-orphans` to ensure a clean shutdown

        Notes:
        - Matching is done using both stack name and compose file path
            to avoid interfering with unrelated stacks
        """
        remote_stack_dir = remote_path(self.name)
        sudo_docker = dget("docker_use_sudo", True)

        # -------------------------
        # Check if stack is running
        # -------------------------
        output = host.get_fact(
            Command,
            command="docker compose ls --format json",
            _sudo=sudo_docker,
        )
        stacks = json.loads(output)
        is_running = any(
            stack["Name"] == self.name
            and str(stack["Status"]).startswith("running")
            and str(stack["ConfigFiles"]).startswith(str(remote_stack_dir))
            for stack in stacks
        )

        # -------------------------
        # Bring stack down if needed
        # -------------------------
        server.shell(
            name=f"[{self.name}] teardown stack",
            commands=[dedent(f"""
                cd {quote(str(remote_stack_dir))} && \\
                docker compose --env-file stack.env down --remove-orphans
            """).strip()],
            _if=lambda: is_running,
            _sudo=sudo_docker,
        )
