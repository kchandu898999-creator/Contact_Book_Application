from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_classes):
    """Append CSS classes to form fields in templates."""
    existing_classes = field.field.widget.attrs.get("class", "")
    merged = f"{existing_classes} {css_classes}".strip()
    return field.as_widget(attrs={"class": merged})
