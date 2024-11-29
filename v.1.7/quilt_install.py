from typing import List, Optional, Union
import subprocess
import tempfile
import random
import os
from minecraft_launcher_lib._helper import download_file, empty
from minecraft_launcher_lib.exceptions import UnsupportedVersion, VersionNotFound, ExternalProgramError
from minecraft_launcher_lib.quilt import get_latest_loader_version, is_minecraft_version_supported, \
    get_latest_installer_version
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.types import CallbackDict
from minecraft_launcher_lib.utils import is_version_valid


def install_quilt(minecraft_version: str, minecraft_directory: Union[str, os.PathLike], loader_version: Optional[str] = None, callback: Optional[CallbackDict] = None, java: Optional[Union[str, os.PathLike]] = None) -> str:
    """
    Installs the Quilt modloader.

    Example:

    .. code:: python

        minecraft_version = "1.20"
        minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
        minecraft_launcher_lib.quilt.install_quilt(minecraft_version, minecraft_directory)

    :param minecraft_version: A vanilla version that is supported by Quilt
    :param minecraft_directory: The path to your Minecraft directory
    :param loader_version: The Quilt loader version. If not given it will use the latest
    :param callback: The same dict as for :func:`~minecraft_launcher_lib.install.install_minecraft_version`
    :param java: A Path to a custom Java executable
    :raises VersionNotFound: The given Minecraft does not exists
    :raises UnsupportedVersion: The given Minecraft version is not supported by Quilt
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
    installer_download_url = f"https://maven.quiltmc.org/repository/release/org/quiltmc/quilt-installer/{installer_version}/quilt-installer-{installer_version}.jar"

    # Generate a temporary path for downloading the installer
    installer_path = os.path.join(tempfile.gettempdir(), f"quilt-installer-{random.randrange(100, 10000)}.tmp")

    try:
        # Download the installer
        download_file(installer_download_url, installer_path, callback=callback)

        # Run the installer
        callback.get("setStatus", empty)("Running quilt installer")
        command = ["java" if java is None else str(java), "-jar", installer_path, "install", "client", minecraft_version, loader_version, f"--install-dir={path}", "--no-profile"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise ExternalProgramError(command, result.stdout, result.stderr)
    finally:
        # Delete the installer as we don't need them anymore
        if os.path.isfile(installer_path):
            os.remove(installer_path)

    # Install all libs of quilt
    quilt_minecraft_version = f"quilt-loader-{loader_version}-{minecraft_version}"
    install_minecraft_version(quilt_minecraft_version, path, callback=callback)

    return quilt_minecraft_version