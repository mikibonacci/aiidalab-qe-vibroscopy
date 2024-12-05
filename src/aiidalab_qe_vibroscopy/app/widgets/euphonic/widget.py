import ipywidgets as ipw
from aiidalab_qe_vibroscopy.app.widgets.euphonic.model import EuphonicModel
from aiidalab_qe_vibroscopy.app.widgets.euphonic.single_crystal_widget import (
    SingleCrystalFullWidget,
)
from aiidalab_qe_vibroscopy.app.widgets.euphonic.single_crystal_model import (
    SingleCrystalFullModel,
)
from aiidalab_qe_vibroscopy.app.widgets.euphonic.powder_full_widget import (
    PowderFullWidget,
)
from aiidalab_qe_vibroscopy.app.widgets.euphonic.powder_full_model import (
    PowderFullModel,
)


class EuphonicWidget(ipw.VBox):
    """
    Widget for the Euphonic Results
    """

    def __init__(self, model: EuphonicModel, node: None, **kwargs):
        super().__init__(children=[ipw.HTML("Loading Euphonic data...")], **kwargs)
        self._model = model
        self._model.node = node
        self.rendered = False

    def render(self):
        if self.rendered:
            return

        self.rendering_results_button = ipw.Button(
            description="Initialise INS data",
            icon="pencil",
            button_style="primary",
            layout=ipw.Layout(width="auto"),
        )
        self.rendering_results_button.on_click(
            self._on_rendering_results_button_clicked
        )

        self.tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )
        self.tabs.observe(
            self._on_tab_change,
            "selected_index",
        )

        self.children = [
            ipw.HBox(
                [
                    ipw.HTML("Click the button to initialise the INS data."),
                    self.rendering_results_button,
                ]
            )
        ]

        self.rendered = True
        self._model.fetch_data()
        # self.render_widgets()

    def _on_rendering_results_button_clicked(self, _):
        self.children = []
        tab_data = []

        single_crystal_model = SingleCrystalFullModel()
        single_crystal_widget = SingleCrystalFullWidget(
            model=single_crystal_model,
            node=self._model.node,
        )
        # We need to link the q_path and fc from the EuphonicModel to the SingleCrystalModel
        single_crystal_widget._model.q_path = self._model.q_path
        single_crystal_widget._model.fc = self._model.fc

        powder_model = PowderFullModel()
        powder_widget = PowderFullWidget(
            model=powder_model,
            node=self._model.node,
        )
        qplane_widget = ipw.HTML("Q-plane view data")
        tab_data.append(("Single crystal", single_crystal_widget))
        tab_data.append(("Powder", powder_widget))
        tab_data.append(("Q-plane view", qplane_widget))
        # Assign children and titles dynamically
        self.tabs.children = [content for _, content in tab_data]

        for index, (title, _) in enumerate(tab_data):
            self.tabs.set_title(index, title)

        self.children = [self.tabs]
        self.tabs.selected_index = 0

    def _on_tab_change(self, change):
        if (tab_index := change["new"]) is None:
            return
        self.tabs.children[tab_index].render()  # type: ignore
