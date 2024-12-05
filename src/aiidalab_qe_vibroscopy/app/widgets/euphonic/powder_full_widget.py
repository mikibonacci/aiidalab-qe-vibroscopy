import ipywidgets as ipw
from aiidalab_qe_vibroscopy.app.widgets.euphonic.powder_full_model import (
    PowderFullModel,
)


class PowderFullWidget(ipw.VBox):
    def __init__(self, model: PowderFullModel, node: None, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading Powder data...")],
            **kwargs,
        )
        self._model = model
        self._model.vibro = node
        self.rendered = False

    def render(self):
        if self.rendered:
            return

        self.children = [ipw.HTML("Here goes widgets for Powder data")]

        self.rendered = True

    #     self._model.fetch_data()
    #     self._needs_powder_widget()
    #     self.render_widgets()

    # def _needs_powder_widget(self):
    #     if self._model.needs_powder_tab:
    #         self.powder_model = PowderModel()
    #         self.powder_widget = PowderWidget(
    #             model=self.powder_model,
    #             node=self._model.vibro,
    #         )
    #         self.children = (*self.children, self.powder_widget)

    # def render_widgets(self):
    #     if self._model.needs_powder_tab:
    #         self.powder_widget.render()
