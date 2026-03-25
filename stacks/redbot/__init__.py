from deploy.utils.stacks import StackBase

REDBOT = StackBase(
    "redbot",
    # directories=[
    #     Directory("config"),
    # ],
    # static_files=[
    #     FileCopy("config/config.yaml", "config/config.yaml"),
    #     FileCopy("config/traefik.env", "config/traefik.env"),
    #     FileCopy(None, "config/acme.json", "600"),
    # ],
)
