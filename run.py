import os
import sys

import netmesh_rfc6349_app.main.utils.pysideflask_ext as pysideflask_ext

from netmesh_rfc6349_app import create_app
from netmesh_rfc6349_app.main.utils.netmesh_installer import check_app_latest_version
from netmesh_rfc6349_app.main.utils.laptop_info import get_downloads_folder_path


def run_on_desktop():
    app = create_app()

    # if getattr(sys, 'frozen', False):
    #     import pyi_splash

    # if getattr(sys, 'frozen', False):
    #     pyi_splash.update_text("Checking update...")

    has_update, current_version, latest_version = check_app_latest_version(app)
    app_version = current_version

    # if getattr(sys, 'frozen', False):
    #     pyi_splash.update_text("Opening the app...")

    pysideflask_ext.init_gui(application=app, port=5000, width=1440, height=900,
                             window_title=f'{app.config["APP_TITLE"]} ({app_version})',
                             has_update=has_update, latest_version=latest_version, download_path=get_downloads_folder_path())
    sys.exit()


def run_in_browser():
    app = create_app()

    app.run(debug=True)


if __name__ == '__main__':
    user_id = os.geteuid()
    if not user_id == 0:
        print(
            f"Run this script as root :)\nRun: sudo python3 {os.path.basename(__file__)}")
    else:
        choices = ['web', 'desktop']
        run_on = sys.argv[1] if len(sys.argv) > 1 else ""

        if not run_on in choices:
            if getattr(sys, 'frozen', False):
                run_on_desktop()
            else:
                run_in_browser()
        else:
            if run_on == 'desktop':
                run_on_desktop()
            else:
                run_in_browser()
