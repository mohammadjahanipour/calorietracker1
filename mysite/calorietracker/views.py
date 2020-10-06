from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, CreateView, FormView, UpdateView
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, LogForm
from .models import Log, Setting
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput

from chartjs.views.lines import BaseLineChartView

from .utilities import *
from datetime import date
import json
from django.core.serializers.json import DjangoJSONEncoder


class UpdateLogData(LoginRequiredMixin, UpdateView):
    """docstring for UpdateLogData."""

    # TODO: check if date does not overlap with existing log

    template_name = "calorietracker/update_logdata.html"
    model = Log
    fields = (
        "date",
        "weight",
        "calories_in",
        "calories_out",
        "activity_lvl",
    )

    success_url = reverse_lazy("analytics")

    def get_form(self):
        form = super().get_form()
        form.fields["date"].widget = DatePickerInput()
        return form


class Settings(LoginRequiredMixin, UpdateView):

    model = Setting
    fields = ["age", "sex", "height", "activity", "goal", "goal_weight", "goal_date"]
    template_name = "calorietracker/settings.html"
    success_url = reverse_lazy("settings")

    def get_object(self):
        return self.request.user.setting

    def get_form(self):
        form = super().get_form()
        form.fields["goal_date"].widget = DateTimePickerInput()
        return form


class HomePage(TemplateView):
    def get(self, request, *args, **kwargs):
        """
        method only servers to run code for testing
        """
        return super().get(request, *args, **kwargs)

    template_name = "calorietracker/home.html"


class Profile(TemplateView):
    template_name = "calorietracker/profile.html"


class Analytics(LoginRequiredMixin, TemplateView):
    template_name = "calorietracker/analytics.html"

    def load_data(self, **kwargs):
        self.query_set = (
            Log.objects.all()
            .filter(user=self.request.user)
            .values("date", "weight", "calories_in")
        )
        df_query = pd.DataFrame(list(self.query_set))
        settings_set = Setting.objects.all().filter(user=self.request.user).values()
        df_settings = pd.DataFrame(list(settings_set))

        # age, height, sex, activity, goaldate, goalweight
        self.age = df_settings["age"]
        self.height = df_settings["height"]
        self.sex = df_settings["sex"].all()
        self.activity = df_settings["activity"].all()
        self.goaldate = df_settings["goal_date"][0].date()
        self.goalweight = round(float(int(df_settings["goal_weight"])), 1)
        self.goal = df_settings["goal"].all()

        # weights, calories_in, dates
        self.weights = df_query["weight"].tolist()
        self.calories_in = df_query["calories_in"].tolist()
        self.dates = df_query["date"].tolist()

        if len(self.weights) < 5:
            self.currentweight = self.weights[-1]
        else:
            self.currentweight = moving_average(self.weights)[-1]

        # Load the date range as self.n
        if self.request.method == "GET":
            rangeDrop_option = self.request.GET.get("rangeDrop", False)
            if rangeDrop_option in ["7", "14", "31"]:
                self.n = int(rangeDrop_option)
            else:
                self.n = len(self.weights)

        # Calculate TDEE
        if len(self.weights) < 10:
            # Not enough data to accurately calculate TDEE using weight changes vs calories in, so we use Harris-Benedict formula
            self.TDEE = self.HarrisBenedict()
        else:
            # Enough data to accurately calculate TDEE using weight changes vs calories in
            self.TDEE = calculate_TDEE(
                self.calories_in, self.weights, n=self.n, smooth=True, window=3,
            )

        # Weight change
        self.weightchangeraw = weight_change(self.weights, n=self.n, smooth=False)
        self.weightchangesmooth = weight_change(self.weights, n=self.n, smooth=True)

        # Weight change rate
        self.dailyweightchange = round(self.weightchangesmooth / self.n, 2)
        if len(self.weights) > 7:
            self.weeklyweightchange = round(self.dailyweightchange * 7, 2)
        else:
            self.weeklyweightchange = "TBD"

        # Progress timeleft, weight to go
        self.timeleft = (self.goaldate - date.today()).days
        self.weighttogo = round(self.goalweight - self.currentweight, 1)
        self.weighttogoabs = abs(self.weighttogo)

        # Targets
        self.targetweeklydeficit = round((self.weighttogo / self.timeleft) * 7, 2)
        self.targetdailycaldeficit = self.targetweeklydeficit * 3500 / 7
        self.dailycaltarget = round(abs(self.TDEE) + self.targetdailycaldeficit)

        # Time to goal
        if len(self.weights) > 1:
            self.currenttimetogoal = abs(
                round((self.weighttogo) / (self.dailyweightchange), 0)
            )
        else:
            self.currenttimetogoal = "TBD"
        self.percenttogoal = round(
            100 * (1 - abs(self.weighttogo / (self.weights[0] - self.goalweight)))
        )
        if self.percenttogoal < 0:
            self.percenttogoal = 0
        elif self.percenttogoal < 1.5:
            self.percenttogoal = 100

    def dispatch(self, request):

        if not self.request.user.is_authenticated:
            return redirect(reverse_lazy("login"))
        if not Log.objects.filter(user=self.request.user).exists():
            messages.info(request, "You need to have made at least one log entry")
            return redirect(reverse_lazy("logdata"))

        settings_vars = [
            "age",
            "sex",
            "height",
            "activity",
            "goal",
            "goal_weight",
            "goal_date",
        ]
        for var in settings_vars:
            print("checking for", var)
            if not (
                list(Setting.objects.filter(user=self.request.user).values(var))[0][var]
            ):
                messages.info(request, "Please fill out your settings. Missing: " + var)
                return redirect(reverse_lazy("settings"))
        return super().dispatch(request)

    def HarrisBenedict(self, **kwargs):
        # Estimate TDEE in the absence of enouhg data
        if self.sex == "M":
            BMR = round(
                -1
                * float(
                    88.362
                    + (13.397 * unit_conv(self.weights[-1], "lbs"))
                    + (4.799 * unit_conv(self.height, "in"))
                    - (5.677 * self.age)
                ),
            )
        elif self.sex == "F":
            BMR = round(
                -1
                * float(
                    447.593
                    + (9.247 * unit_conv(self.weights[-1], "lbs"))
                    + (3.098 * unit_conv(self.height, "in"))
                    - (4.330 * self.age)
                ),
            )
        if self.activity == "1":
            TDEE = BMR * 1.2
        elif self.activity == "2":
            TDEE = BMR * 1.375
        elif self.activity == "3":
            TDEE = BMR * 1.55
        elif self.activity == "4":
            TDEE = BMR * 1.725
        elif self.activity == "5":
            TDEE = BMR * 1.9

        return round(TDEE)

    def get_pie_chart_data(self):
        TDEE = abs(self.TDEE)
        dailycaltarget = abs(self.dailycaltarget)
        calories_in = self.calories_in[-self.n :]
        if self.goal == "L" or self.goal == "M":
            pie_labels = [
                "Days Above TDEE",
                "Days Below Target",
                "Days Above Target but Below TDEE",
            ]
            pie_red = len([i for i in calories_in if (i > TDEE)])
            pie_green = len([i for i in calories_in if i < dailycaltarget])
            pie_yellow = len([i for i in calories_in if (dailycaltarget < i < TDEE)])

        elif self.goal == "G":
            pie_labels = [
                "Days Below TDEE",
                "Days Above Target",
                "Days Above TDEE but Below Target",
            ]
            pie_red = len([i for i in calories_in if (i < TDEE)])
            pie_green = len([i for i in calories_in if i > dailycaltarget])
            pie_yellow = len([i for i in calories_in if (TDEE < i < dailycaltarget)])

        return pie_labels, pie_red, pie_yellow, pie_green

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.load_data()
        if abs(self.targetweeklydeficit) > 2:
            messages.info(
                self.request,
                "Warning: Your goal weight and/or date are very aggressive. We recommend setting goals that require between -2 to 2 lbs (-1 to 1 kgs) of weight change per week.",
            )

        # TODO: HANDLE UNITS CONVERSION FOR UI/FRONT END

        context = {
            "units_weight": "lbs",
            "n": self.n,
            "TDEE": self.TDEE,
            "weight_change_raw": self.weightchangeraw,
            "weight_change_smooth": self.weightchangesmooth,
            "daily_weight_change": self.dailyweightchange,
            "weekly_weight_change": self.weeklyweightchange,
            "goal_date": self.goaldate.strftime("%b-%-d"),
            "time_left": self.timeleft,
            "goal_weight": self.goalweight,
            "current_weight": self.currentweight,
            "weight_to_go": self.weighttogo,
            "weight_to_go_abs": self.weighttogoabs,
            "target_weekly_deficit": self.targetweeklydeficit,
            "target_daily_cal_deficit": self.targetdailycaldeficit,
            "daily_cal_target": self.dailycaltarget,
            "current_time_to_goal": self.currenttimetogoal,
            "percent_to_goal": self.percenttogoal,
            "data_weight": self.weights[-self.n :],
            "data_cal_in": self.calories_in[-self.n :],
            "data_date": json.dumps(
                [date.strftime("%b-%d") for date in self.dates][-self.n :]
            ),
            "json_data": json.dumps(
                {"data": list(self.query_set)[-self.n :]},
                sort_keys=True,
                indent=1,
                cls=DjangoJSONEncoder,
            ),
        }

        # Populate red, green, yellow for pie chart
        (
            context["pie_labels"],
            context["pie_red"],
            context["pie_yellow"],
            context["pie_green"],
        ) = self.get_pie_chart_data()

        return context


class LineChartJSONView(BaseLineChartView):
    pass


line_chart = TemplateView.as_view(template_name="line_chart.html")
line_chart_json = LineChartJSONView.as_view()


class LogData(LoginRequiredMixin, CreateView):
    model = Log
    form_class = LogForm
    template_name = "calorietracker/logdata.html"
    success_url = reverse_lazy("analytics")

    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class Register(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy("login")
    template_name = "calorietracker/register.html"


class Login(LoginView):
    form_class = LoginForm
    template_name = "calorietracker/login.html"


class Logout(LogoutView):
    """Logout"""


class PasswordChange(PasswordChangeView):
    """PasswordChange"""

    success_url = reverse_lazy("home")
    template_name = "calorietracker/change-password.html"
