from django.shortcuts import render
from .disk_math import generate_figures

def index(request):
    context = {}
    if request.method == 'POST':
        func_str = request.POST.get('function')
        a = float(request.POST.get('a'))
        b = float(request.POST.get('b'))

        try:
            volume, fig1, fig2, fig3 = generate_figures(func_str, a, b)
            context = {
                'volume': f"The volume is {volume:.4f}",
                'function_fig': fig1,
                'solid_fig': fig2,
                'solid_2d_fig': fig3,
                'input': {'function': func_str, 'a': a, 'b': b}
            }
        except Exception as e:
            context['error'] = f"Error: {e}"

    return render(request, 'calculator/index.html', context)
