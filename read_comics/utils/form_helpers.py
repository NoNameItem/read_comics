from crispy_forms.helper import FormHelper


class DefaultFormHelper(FormHelper):
    def __init__(self, form=None):
        super().__init__(form)
        self.include_media = False
        self.action = ""
        self.use_custom_control = False
