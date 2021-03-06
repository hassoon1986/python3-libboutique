import gi

gi.require_version("Snapd", '1')
from gi.repository import Snapd

from libboutique.services.common.base_package_service import BasePackageService


class SnapService(BasePackageService):

    def __init__(self, progress_publisher=None):
        self.snap_client = Snapd.Client().new()
        self.channel = "stable"
        self.package_type = "snap"
        self.progress_publisher = progress_publisher

    def progress_callback(self, client, change, deprecated, user_data):
        if self.progress_publisher is None: return
        total = 0
        done = 0
        for task in change.get_tasks():
            total += task.get_progress_total()
            done += task.get_progress_done()
        percent = round((done/total) * 100)
        self.progress_publisher.publish(client, {"percent": percent, "total": total, "done": done})

    def install_package(self, name):
        try:
            if self.snap_client.install2_sync(flags=0, name=name, channel=self.channel, progress_callback=self.progress_callback):
                return self._successful_message(action="install", package=name)
        except Exception as ex:
            return self._format_glib_error(exception=ex)

    def remove_package(self, name):
        try:
            if self.snap_client.remove_sync(name=name, progress_callback=self.progress_callback):
                return self._successful_message(action="remove", package=name)
        except Exception as ex:
            return self._format_glib_error(exception=ex)

    def get_installed_package(self):
        installed_snaps = self.snap_client.list_sync()
        return self._create_dict_from_array(snap_array=installed_snaps)

    def retrieve_package_information_by_name(self, name):
        snap = self.snap_client.find_sync(flags=Snapd.FindFlags(1), query=name)
        return self._create_dict_from_array(snap[0]) # ( [ Snaps ], suggested_currency: )

    def _create_dict_from_array(self, snap_array):
        packages = []
        for snap in snap_array:
            packages.append(self._extract_snap_to_dict(snap=snap))
        return packages

    def _extract_snap_to_dict(self, snap):
        return {
            "id": snap.get_id(),
            "name": snap.get_name(),
            "type": self.package_type,
            "revision": snap.get_revision(),
            "license": snap.get_license(),
            "icon": snap.get_icon(),
            "download_size": snap.get_download_size(),
            "install_date": snap.get_install_date()
        }


