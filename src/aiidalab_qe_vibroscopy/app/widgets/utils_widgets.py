import ipywidgets as ipw

from aiidalab_qe.common.infobox import InfoBox


class SettingsInfoBoxWidget(ipw.VBox):
    """Infobox widget for settings.

    Please note that you need also to put explicitly the infobox in the children list of the host widget
    (e.g. another box).
    This is particularly convenient when the appearing infobox is meant to appear somewhere else (e.g. in a VBox
    instead of a HBox).
    """

    def __init__(self, description: str = "", info: str = "", **kwargs):
        super().__init__(**kwargs)

        self.about_toggle = ipw.ToggleButton(
            layout=ipw.Layout(width="auto"),
            button_style="info",
            icon="info",
            value=False,
            description=description,
            tooltip="Info on these settings",
            disabled=False,
        )

        self.infobox = InfoBox(
            children=[ipw.HTML(info)],
        )
        ipw.dlink(
            (self.about_toggle, "value"),
            (self.infobox, "layout"),
            lambda x: {"display": "block"} if x else {"display": "none"},
        )

        self.children = [
            ipw.HBox([self.about_toggle]),
            # self.infobox
        ]
