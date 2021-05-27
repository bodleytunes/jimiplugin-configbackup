from core import plugin, model


class _configbackup(plugin._plugin):
    version = 0.4

    def install(self):
        # Register batfish Models

        model.registerModel(
            "cfgBackupConnect",
            "_cfgBackupConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.registerModel(
            "cfgBackupSave",
            "_cfgBackupSave",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.registerModel(
            "cfgBackupGitops",
            "_cfgBackupGitops",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.registerModel(
            "cfgBackupFortigateConnect",
            "_cfgBackupFortigateConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        return True

    def uninstall(self):
        # de-register batfish Models

        model.deregisterModel(
            "cfgBackupConnect",
            "_cfgBackupConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.deregisterModel(
            "cfgBackupSave",
            "_cfgBackupSave",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.deregisterModel(
            "cfgBackupGitops",
            "_cfgBackupGitops",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.deregisterModel(
            "cfgBackupFortigateConnect",
            "_cfgBackupFortigateConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        return True

    def upgrade(self, LatestPluginVersion):

        if self.version < 0.1:
            model.registerModel(
                "cfgBackupConnect",
                "_cfgBackupConnect",
                "_action",
                "plugins.configbackup.models.action",
            )
        if self.version < 0.2:
            model.registerModel(
                "cfgBackupSave",
                "_cfgBackupSave",
                "_action",
                "plugins.configbackup.models.action",
            )
        if self.version < 0.3:
            model.registerModel(
                "cfgBackupGitops",
                "_cfgBackupGitops",
                "_action",
                "plugins.configbackup.models.action",
            )
        if self.version < 0.4:
            model.registerModel(
                "cfgBackupFortigateConnect",
                "_cfgBackupFortigateConnect",
                "_action",
                "plugins.configbackup.models.action",
            )
        return True
