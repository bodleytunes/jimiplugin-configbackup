from core import plugin, model


class _configbackup(plugin._plugin):
    version = 0.5

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
            "cfgBackupFortigateConnect",
            "_cfgBackupFortigateConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        # _cfgGitOps
        model.registerModel(
            "cfgGitOps",
            "_cfgGitOps",
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
            "cfgBackupFortigateConnect",
            "_cfgBackupFortigateConnect",
            "_action",
            "plugins.configbackup.models.action",
        )
        model.deregisterModel(
            "cfgGitOps",
            "_cfgGitOps",
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
        if self.version < 0.4:
            model.registerModel(
                "cfgBackupFortigateConnect",
                "_cfgBackupFortigateConnect",
                "_action",
                "plugins.configbackup.models.action",
            )
        if self.version < 0.5:
            model.registerModel(
                "cfgGitOps",
                "_cfgGitOps",
                "_action",
                "plugins.configbackup.models.action",
            )
        return True
