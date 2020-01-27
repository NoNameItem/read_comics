class BreadcrumbMixin:
    breadcrumb = []

    def get_context_data(self, **kwargs):
        context = super(BreadcrumbMixin, self).get_context_data(**kwargs)
        context['breadcrumb'] = self.get_breadcrumb()
        return context

    def get_breadcrumb(self):
        if self.breadcrumb:
            return self.breadcrumb
        else:
            return []
