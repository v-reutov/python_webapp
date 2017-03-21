class ExtraContext(object):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContext, self).get_context_data(**kwargs) #pylint: disable=E1101
        context.update(self.extra_context)
        return context
