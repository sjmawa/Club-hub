from django import forms 
from events.models import Event

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widget()
    default_classes = "block border-2 border-gray-300 p-3 w-full rounded-lg shadow-md focus:outline-none focus:border-rose-500 focus:ring-rose-500"
    def apply_styled_widget(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.URLInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f"Enter {field.label.lower() if field.label else field_name} URL",
                    'type': 'url',
                    'pattern': 'https?://.*',
                })
            elif isinstance(field.widget, forms.EmailInput):
                print("inside email")
                field.widget.attrs.update({
                'class': self.default_classes,
                "placeholder": f"Enter {field.label.lower() if field.label else field_name}",
                "type": "email"
                })
            elif isinstance(field.widget, forms.TextInput):
                print("inside textinput")
                field.widget.attrs.update({
                    'class': self.default_classes,
                    "placeholder":f" Enter {field.label.lower() if field.label else field_name}",
                })
            elif isinstance(field.widget, forms.Textarea):
                print("inside textarea")
                field.widget.attrs.update({
                    'class': self.default_classes,
                    "placeholder":f" Enter {field.label.lower() if field.label else field_name}",
                    'rows':5
                })
            elif isinstance(field.widget, forms.SelectDateWidget):
                print("inside date")
                field.widget.attrs.update({
                    'class': "border-2 border-gray-300 p-3 rounded-lg shadow-md focus:outline-none focus:border-rose-500 focus:ring-rose-500"
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                'class': self.default_classes,
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                print("inside checkbox")
                field.widget.attrs.update({
                    'class': "space-y-2"
                })
            elif isinstance(field.widget, forms.CheckboxInput):
               field.widget.attrs.update({
                    'class': "h-5 w-5 text-rose-500 rounded focus:ring-rose-500 cursor-pointer",
                })
            else:
                print("inside else")
                field.widget.attrs.update({
                    'class': self.default_classes
                })

class EventForm(StyledFormMixin, forms.ModelForm):
    date = forms.DateField(
        label="Event Date",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    time = forms.TimeField(
        label="Event Time",
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    class Meta:
        model = Event
        fields = [
            'title','description','event_type','club','date','time','location',
            'image','max_capacity','is_online','notice','website','facebook'
        ]
