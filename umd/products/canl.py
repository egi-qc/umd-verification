from umd import base


canl = base.Deploy(
    name="canl",
    doc="Canl installation.",
    metapkg=[
        "canl-c",
        "canl-c++",
        "canl-java",
    ])
