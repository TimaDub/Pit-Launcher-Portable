from typing import List, Optional, Union
import subprocess
import tempfile
import random
import os
from minecraft_launcher_lib._helper import download_file, empty
from minecraft_launcher_lib.exceptions import UnsupportedVersion, VersionNotFound, ExternalProgramError
from minecraft_launcher_lib.fabric import get_latest_loader_version, is_minecraft_version_supported, \
    get_latest_installer_version
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.types import CallbackDict
from minecraft_launcher_lib.utils import is_version_valid


def install_fabric(minecraft_version: str, minecraft_directory: Union[str, os.PathLike], loader_version: Optional[str] = None, callback: Optional[CallbackDict] = None, java: Optional[Union[str, os.PathLike]] = None) -> str:
    """
    Installs the Fabric modloader.
    For more information take a look at the :doc:`tutorial </tutorial/install_fabric>`.

    Example:

    .. code:: python

        minecraft_version = "1.20"
        minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        minecraft_launcher_lib.fabric.install_fabric(minecraft_version, minecraft_directory)

    :param minecraft_version: A vanilla version that is supported by Fabric
    :param minecraft_directory: The path to your Minecraft directory
    :param loader_version: The fabric loader version. If not given it will use the latest
    :param callback: The same dict as for :func:`~minecraft_launcher_lib.install.install_minecraft_version`
    :param java: A Path to a custom Java executable
    :raises VersionNotFound: The given Minecraft does not exists
    :raises UnsupportedVersion: The given Minecraft version is not supported by Fabric
    """
    path = str(minecraft_directory)
    if not callback:
        callback = {}

    # Check if the given version exists
    if not is_version_valid(minecraft_version, minecraft_directory):
        raise VersionNotFound(minecraft_version)

    # Check if the given Minecraft version supported
    if not is_minecraft_version_supported(minecraft_version):
        raise UnsupportedVersion(minecraft_version)

    # Get latest loader version if not given
    if not loader_version:
        loader_version = get_latest_loader_version()

    # Make sure the Minecraft version is installed
    install_minecraft_version(minecraft_version, path, callback=callback)

    # Get installer version
    installer_version = get_latest_installer_version()
    installer_download_url = f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/{installer_version}/fabric-installer-{installer_version}.jar"

    # Generate a temporary path for downloading the installer
    installer_path = os.path.join(tempfile.gettempdir(), f"fabric-installer-{random.randrange(100, 10000)}.tmp")

    # Download the installer
    download_file(installer_download_url, installer_path, callback=callback)

    # Run the installer see https://fabricmc.net/wiki/install#cli_installation
    callback.get("setStatus", empty)("Running fabric installer")
    command = ["java" if java is None else str(java), "-jar", installer_path, "client", "-dir", path, "-mcversion", minecraft_version, "-loader", loader_version, "-noprofile", "-snapshot"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise ExternalProgramError(command, result.stdout, result.stderr)

    # Delete the installer we don't need them anymore
    os.remove(installer_path)

    # Install all libs of fabric
    fabric_minecraft_version = f"fabric-loader-{loader_version}-{minecraft_version}"
    install_minecraft_version(fabric_minecraft_version, path, callback=callback)

    return fabric_minecraft_version