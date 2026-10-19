from pathlib import Path
import subprocess


def run_setup() -> None:
    """Run the package installation script and prepare the local PATH."""
    install_sh = Path(__file__).parent / "install.sh"

    # Add ~/.local/bin to PATH for future shell sessions.
    bashrc = Path.home() / ".bashrc"
    path_line = 'export PATH="$HOME/.local/bin:$PATH"'

    if bashrc.exists():
        content = bashrc.read_text()
    else:
        content = ""

    if path_line not in content:
        with bashrc.open("a") as f:
            f.write(f"\n{path_line}\n")

    subprocess.run(
        f"sudo dos2unix '{install_sh}' && sudo chmod +x '{install_sh}' && sudo '{install_sh}'",
        shell=True,
        check=True,
    )


def main() -> None:
    """Entry point for the ``raspi-usb-sim-setup`` console script."""
    run_setup()
