#!/usr/bin/env python
# %% [markdown]
# # Тестирование рекомендаций на реальных пользователях
#
# Раздел финального проекта об A/B тестировании
# %% [markdown]
# ## Резюме.
#
# - Для A/B теста [необходимо по меньшей мере 6702 клиента](#plan_formula) в
#   тестовой группе и столько же в контрольной.  Использованная выборка (8847 клиентов
#   в тестовой группе и 8732 в контрольной) достаточна для получения значимого результата.
#   
# - Тестирование показало [статистически значимую разницу](#ssi_test_pvalue)
#   в конверсии между группами, можно считать тест успешным и распространять
#   систему рекомендаций на всех пользователей.

# %% [markdown]
# ### Содержание <a name='contents'/>
# 
# * [ Планирование эксперимента (сплит-теста)](#plan)
#   - [История вопроса](#plan_history)
#   - [Немного о планировании эксперимента](#plan_count)
#   - [Онлайн калькуляторы](#plan_calculators)
#   - [Расчёт необходимого размера выборки для A/B теста](#plan_compute)
#     + [Быстрая прикидка по формуле Лера](#plan_lehr)
#     + [Более точный расчёт по формуле](#plan_formula)
#     + [Источники](#plan_links)
# * [Определение статистической значимости](#significance)
#   - [Определяем 95% доверительные интервалы для среднего в тестовой и контрольной группах.](#sign_ci)
#   - [Расчёт статистической значимости (p-value)](#ssi_test_pvalue)
#     + [Источники](#si_links)

# %% [markdown]
# Код в этом документе по умолчанию скрыт (после первого запуска).
# Для того, чтобы показать код, нажмите кнопку ниже.

# %%
from IPython.display import HTML
HTML('''<script>
  function code_toggle() {
    if (code_shown){
      $('div.input').hide('500');
      $('#toggleButton').val('Show Code')
    } else {
      $('div.input').show('500');
      $('#toggleButton').val('Hide Code')
    }
    code_shown = !code_shown
  }

  $( document ).ready(function(){
    code_shown=false;
    $('div.input').hide()
  });
</script>
<form action="javascript:code_toggle()"><input type="submit" id="toggleButton" value="Show Code"></form>
''')

# %% [markdown]
# ##  Планирование эксперимента (сплит-теста) <a name='plan'/>
#
# ### История вопроса <a name='plan_history'/>
# 
# Спустя месяц на сайте реализована новая функциональность с предложением добавить
# в корзину второй подходящий курс. Ваши коллеги хотят оценить эффективность этой
# функции и качество подбора рекомендаций.

# Для этого запускается сплит-тест, где все клиенты случайным образом делятся на
# контрольную и тестовую группу. Тестовой группе показываются рекомендации, а
# контрольной — нет.

# До реализации рекомендаций средняя конверсия в покупку второго курса была 3,2%. Вы
# ожидаете, что ввод рекомендаций сможет подрастить её до 4%
#
# Вопрос: сколько клиентов должно быть в каждой из групп для A/B теста.

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %% [markdown]
# ### Немного о планировании эксперимента <a name="plan_count"/>

# %% [markdown]
# Перед тем, как что-то делать, нужно определить требуемый масштаб эксперимента — может быть,
# и нет смысла его проводить.
# Наши данные: конверсия в покупку второго курса _была_ 3.2%, _ожидается_ рост до 4%.  Хотя разница
# всего 0.8 _процентного пункта_, это рост конверсии на _25%_ — (${0.4-0.32})/{0.32} = 0.25$.
#
# Согласно общепринятому стандарту, нужно показать, что мы с вероятностью 80% заметим изменение,
# причём оно будет статистически достоверно на уровне 95%.
#
# Наши гипотезы и возможные ошибки:
# - нулевая — выдача рекомендаций не влияет на конверсию,
# - альтернативная — выдача рекомендаций _повышает_ конверсию (односторонний тест).
#
# - Ошибка первого рода: утверждать, что повышение конверсии есть, хотя на самом деле его нет (т.&nbsp;е. верна нулевая гипотеза) — FP.
# - Ошибка второго рода: считать, что повышения конверсии нет, хотя в реальности оно есть — FN.
#
# Нужно ограничить вероятность ошибки первого рода 5%, а второго рода 20%. Конечно, нельзя забывать и о
# минимально достаточном числе наблюдений для расчёта статистических параметров для пропорций —
# и «успехов», и «неудач» должно быть не менее 15.
# 
# Сразу расчитаю, сколько должно быть в каждой группе событий, чтобы это выполнялось: $15 \times 0.032 + 1 \approx 470 $.
# Но такого числа не хватит для критериев значимости и мощности.
# 
# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %%
import numpy as np
from scipy.stats import norm
from collections import namedtuple
from math import sqrt, ceil
from scipy.stats import binom
import matplotlib.pyplot as plt

# %% [markdown]
# ### Онлайн калькуляторы <a name='plan_calculators'/>
 
# %% [markdown]
#
# [Онлайн калькулятор](https://juliasilge.shinyapps.io/power-app/) говорит, что при статистической
# мощности в 80%, уровне значимости 5% и базовой конверсии 3% требуется выборка в 9000 событий
# в каждой группе.
#
# [Другой онлайн-калькулятор](https://abtestguide.com/calc/?ua=7000&ub=7000&ca=224&cb=280&pre=1&up=25)
# считает, что при этих условиях достаточно выборки в 7000 событий в каждой группе.
#
# [Ещё один полезный калькулятор](https://win-vector.shinyapps.io/CampaignPlanner_v3/) показывает нам, что
# чем больше выборка, тем меньше площадь под пересекающимися частями кривых распределений.
#
# Предположения:
#   - Клиенты делают свои покупки независимо друг от друга.
#   - За время тестов поведение клиентов не изменяется (предположение статичной ситуации)

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %% [markdown]
# ### Расчёт необходимого размера выборки для A/B теста <a name='plan_compute'/>

# %% [markdown]
# Поскольку калькуляторы дали нам разные цифры,
# выполню собственный расчёт.  Исходные данные:
# 
# * Базовая конверсия — 3.2% или 0.032
# * Ожидаемый эффект положительный, 0.8 процентных пункта (рост конверсии до 0.04).
# * Требуемая статистическая значимость 95%, или 5% вероятности FP.
# * Требуемая статистическая мощность 80%, или 20% вероятности FN.

# %% [markdown]
# #### Быстрая прикидка по формуле Лера <a name='plan_lehr'/>

# %% [markdown]
# Роберт Лер (Robert Lehr) предложил простую формулу для оценки размера выборки
# в _двустороннем_ тесте при уровне значимости 0.05 и статистической мощности 80%:
# $n = 16 \times s^2/d^2$, где $s$ — стандартная ошибка в выборке, и $d$ — ожидаемая
# разница. Заменяя $s^2$ на $\bar{p}\cdot(1-\bar{p})$, получаем:
# $n = 16 \times \bar{p} \cdot (1-\bar{p}) / (p_1-p_2)^2$.
# Подставляем числа:
#
# $$
# \bar{p} = (0.032 + 0.04)/2 = 0.036
# $$
#
# $$
# n = 16 \times \frac{\bar{p} \cdot (1 - \bar{p})}{(p_1 - p_2)^2} = \frac{16 \times (0.036 \times 0.0964)}{0.008^2} = 8676
# $$

# %%
print("Требуемый размер каждой группы по формуле Лера:", ceil(16 * (0.036 * 0.964) / 0.008**2))

# %% [markdown]
# Учитывая, что формула Лера для двустороннего случая, можно считать полученное
# число оценкой «сверху»


# %% [markdown]
# #### Более точный расчёт по формуле <a name='plan_formula'/>

# %% [markdown]
# Базовая формула определения минимальной выборки для одностороннего теста:
# 
# $$
# n = \frac{(Z_\alpha + Z_{1-\beta})^2 \times ( C_A \cdot (1 - C_A) + C_B \cdot (1 - C_B) )}{(C_A - C_B)^2}
# $$
# где:
#   - $\alpha$ — расчётная вероятность ошибки первого рода;
#   - $\beta$ — расчётная вероятность ошибки второго рода;
#   - $C_A$, $C_B$ — конверсии в группах A и B соответственно (в долях единицы).
#

# %% [markdown]
# Z-статистики можем расчитать, воспользовавшись объектом `scipy.stats.norm` , который реализует нормальное  распределение.

# %% 
z_alpha = norm.ppf(0.95)  # 1-side test
z_rev_beta = norm.ppf(0.8)
conv_a = 0.032
conv_b = 0.04
print(f"Z-статистики: Z_alpha: {z_alpha:.3f}, Z_rev_beta: {z_rev_beta:.3f}.")

# %% [markdown]
# Тогда:
# 
#
# $$
# n = \frac{(Z_{0.95}+Z_{1-0.8})^2  \times ( 0.032 \cdot (1 - 0.032) + 0.04 \cdot (1 - 0.04) )}{(0.032 - 0.04)^2}
# $$

# %%
zeds = (z_alpha + z_rev_beta)**2
bottom = (conv_a - conv_b)**2
sample_size = ceil( zeds * (conv_a * (1 - conv_a) + conv_b * (1 - conv_b)) / bottom )
print(f"В каждой группе должно быть минимум {sample_size} клиентов.")

# %% [markdown]
# Эта формула даёт нам минимум 6702 пользователя в каждой группе (тестовой и контрольной)

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %% [markdown]
# #### Источники <a name='plan_links'/>
# 
# - Lehr R. Sixteen s squared over d squared: a relation for crudesample size estimates // Statistics in Medicine, 1992, 11. – P. 1099-1102.
# - [Определение требуемого числа исследуемых](https://medstatistic.ru/calculators/calcsize.html)
# - [Описание выбора размера теста на SplitMetrics](https://splitmetrics.com/blog/mobile-a-b-testing-sample-size/).
# - Гайд по [выбору размера теста](https://www.convertize.com/ab-testing-sample-size/) на Convertize.com.
# - [Khalid Saleh. Calculating Sample Size For An AB Test](https://www.invespcro.com/blog/calculating-sample-size-for-an-ab-test/)

# %% [markdown]
# ## Определение статистической значимости <a name='significance'/>

# %% [markdown]
# Входные данные:
# 
#  - Контрольная группа: 8732 клиента, 293 повторных покупки (=успеха).
#  - Тестовая группа: 8847 клиентов, 347 повторных покупок.
#  - Требуемая статистическую значимость 95% (p-value 0.05)
#  - Доверительные интервалы также буду считать с уровнем значимости 95%.
#
# Объём выборки достаточный и в контрольной, и в тестовой группах. Соотношение количества
# клиентов в группах примерно 50/50.

# %%
# Считаем стандартную ошибку для пропорции
def get_sterr(size: int, success: int) -> float:
    """Расчёт стандартного отклонения для пропорции. Параметры:
    1) размер выборки, 2) количество "успехов"
    Возвращает: стандартную ошибку"""
    p = success / size   # proportion
    return sqrt( (p * (1 - p)) / size )

def _t_get_sterr():
    "unit test for get_strerr function"
    assert(get_sterr(5000, 0) == 0)
    assert(get_sterr(5000, 5000) == 0)
    assert(abs(get_sterr(5000000,2500000) - 2.2e-4) < 1e-5)
    return

Group = namedtuple('Group', ['size', 'success', 'conv_rate', 'stderr'], defaults={'conv_rate':0, 'stderr': 0})
test_g = Group(size=8847, success=347, conv_rate=347/8847, stderr=get_sterr(8847, 347))
ctrl_g = Group(size=8732, success=293, conv_rate=293/8732, stderr=get_sterr(8732, 293))

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %% [markdown]
# ### Определяем 95% доверительные интервалы для среднего в тестовой и контрольной группах. <a name='sign_ci'/>

# %% [markdown]
# Выборки достаточно большие, и повторных покупателей, и однократных больше 15-ти, можем
# использовать формулы нормального распределения при расчёте доверительных
# интервалов пропорций.
#
# Z-статистика, в полосе  между $-Z_\alpha$ до $Z_\alpha$ содержится 95% вероятности при нормальном распределении.
# 
# %%
# приблизительно 1.96
z_alpha = norm.ppf(0.975)

# %% [markdown]
# Соответственно, доверительный интервал 95% для каждой группы будет от `conv_rate - z_alpha * stderr`
# до `conv_rate + z_alpha * stderr`:

# %%
test_conv_int = (test_g.conv_rate - z_alpha * test_g.stderr, test_g.conv_rate + z_alpha * test_g.stderr)
ctrl_conv_int = (ctrl_g.conv_rate - z_alpha * ctrl_g.stderr, ctrl_g.conv_rate + z_alpha * ctrl_g.stderr)
print("""\
Доверительные интервалы 95%:
    Тестовая группа:    от {0:.4f} до {1:.4f},
    Контрольная группа: от {2:.4f} до {3:.4f}.
""".format(test_conv_int[0], test_conv_int[1], ctrl_conv_int[0], ctrl_conv_int[1]))

# %% [markdown]
# Интервалы в некоторой степени пересекаются, это плохой признак с точки зрения вероятности
# случайно получить тестовую выборку при верной нулевой гипотезе.  Скорее всего, и по p-value
# статистической значимости добиться не удастся.
#
# %% [markdown]
# В числах не очень наглядно, покажу распределения графически.
# 
# Взял код [из статьи Nguyen Ngo](https://towardsdatascience.com/the-math-behind-a-b-testing-with-example-code-part-1-of-2-7be752e1d06f)
# и построил распределения возможных пропорций для популяции в целом отдельно для контрольной и тестовой выборок.
#
# %%
fig, ax = plt.subplots(figsize=(12,6))
test_range=np.array(range(200,450,2))
y_ctrl = binom(ctrl_g.size, ctrl_g.conv_rate).pmf(test_range)
ax.bar(test_range, y_ctrl, color='blue', alpha=0.5)
y_test = binom(test_g.size, test_g.conv_rate).pmf(test_range)
ax.bar(test_range, y_test, color='#e0a0a0', alpha=0.5)
plt.xlabel('Converted users')
plt.ylabel('Probability')
plt.show()

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#plan)  |
# |:--------------------------|-------------------------------:|

# %% [markdown]
# Как видим, ближайшие друг к другу части распределений заметно пересекаются.
# С другой стороны, среднее значение для тестовой выборки лежит в области очень
# малых вероятностей, если принять нулевую гипотезу, оно слишком «странное».
# Посмотрим, что нам скажет [расчёт p-value](#ssi_test_pvalue).
# 
# %% [markdown]
# ### Расчёт статистической значимости (p-value) <a name='ssi_test_pvalue'/>
 
# %% [markdown]
# Для расчёта p-value понадобится средняя пропорция и z-статистика разности.
# Считаю среднюю пропорцию:
#
# $$
# \bar{p} = \frac {p_1 \cdot n_1 + p_2 \cdot n_2} {n_1 + n_2} 
# $$

# %%
avg_proportion = (test_g.success + ctrl_g.success) / (test_g.size + ctrl_g.size)
print(f'Средняя пропорция: {avg_proportion:.4f}')

# %% [markdown]
# И Z-статистику:
#
# $$
# Z_{avg} = \frac{p_1 - p_2}{ \sqrt{\bar{p} \cdot (1-\bar{p})} \times \sqrt{1/n_1 + 1/n_2} }
# $$
 
# %%
z_avg = ( (test_g.conv_rate - ctrl_g.conv_rate) /
          ( sqrt(avg_proportion * (1-avg_proportion)) * sqrt(1/test_g.size + 1/ctrl_g.size) ) )
print(f'Z-статистика для расчёта p-value: {z_avg:.4f}')
p_val = 1-norm.cdf(z_avg)
print(f'p-value для рассчитанной Z-статистики:  {p_val:.4f}')


# %% [markdown]
# P-value достаточно мало (меньше 0.05), что даёт нам право утверждать, что различия
# контрольной и тестовой групп __статистически значимы__.

# %% [markdown]
# | [К оглавлению](#contents) | [К началу раздела](#significance)  |
# |:--------------------------|-------------------------------:|
# 
# %% [markdown]
# #### Источники <a name='si_links'/>
#
# - [The math behind a/b testing](https://towardsdatascience.com/the-math-behind-a-b-testing-with-example-code-part-1-of-2-7be752e1d06f)
