from django import forms

from .models import Doacao


class DoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ["doador", "data_doacao", "local", "volume_ml", "observacao"]
        widgets = {
            "data_doacao": forms.DateInput(attrs={"type": "date"}),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }
