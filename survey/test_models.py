from django.test import TestCase
import models
import datetime

class MonthCreationTests(TestCase):

    def test_default_month_values(self):
        models.Month.objects.create(wr_day=datetime.date.today())
        month = models.Month.objects.get(wr_day=datetime.date.today())
        self.assertFalse(month.open_checkin)
        self.assertFalse(month.close_checkin)
        month.delete()

    def test_create_month(self):
        wr_date = datetime.date.today()
        open_date = wr_date - datetime.timedelta(days=1)
        close_date = wr_date + datetime.timedelta(days=1)
        models.Month.objects.create(wr_day=datetime.date.today(),
                                    open_checkin=open_date, 
                                    close_checkin=close_date)
        month = models.Month.objects.get(wr_day=datetime.date.today())
        self.assertEqual(month.open_checkin, open_date)
        self.assertEqual(month.close_checkin, close_date)
        month.delete()


class ModeCreationTests(TestCase):

    def test_default_mode_values(self):
        models.Mode.objects.create(name='default')
        empty = models.Mode.objects.get(name='default')
        self.assertFalse(empty.green)
        self.assertFalse(empty.speed)
        self.assertFalse(empty.carb)
        self.assertFalse(empty.met)
        empty.delete()

    def test_create_mode(self):
        models.Mode.objects.create(name="bike", met=50.0,
                                   carb=0.0, speed=20.0, green=True)
        bike = models.Mode.objects.get(name='bike')
        self.assertEqual(bike.name, 'bike')
        self.assertEqual(bike.speed, 20.0)
        self.assertEqual(bike.carb, 0.0)
        self.assertEqual(bike.met, 50.0)
        self.assertTrue(bike.green)
        bike.delete()


class EmployerTests(TestCase):

    def test_default_employer_values(self):
        models.Employer.objects.create(name="an organization")
        employer = models.Employer.objects.get(name="an organization")
        self.assertEqual(employer.nr_employees, 1)
        self.assertFalse(employer.active2015)
        employer.delete()

    def test_create_employer(self):
        models.Employer.objects.create(name="Company Inc.", nr_employees=5000,
                                       active2015=True)
        employer = models.Employer.objects.get(name="Company Inc.")
        self.assertEqual(employer.name, "Company Inc.")
        self.assertEqual(employer.nr_employees, 5000)
        self.assertTrue(employer.active2015)
        employer.delete()




class CommuterSurveyTests(TestCase):


    def test_default_commutersurvey_values(self):
        pass

    def test_commutersurvey_fields(self):
        name = "Somebody"
        models.Month.objects.create(wr_day=datetime.date.today())
        month = models.Month.objects.get(wr_day=datetime.date.today())
        models.Employer.objects.create(name="Company Inc.", nr_employees=5000,
                                       active2015=True)
        employer = models.Employer.objects.get(name="Company Inc.")
        email = "somebody@email.com"
        home_address = "Somewhere Street"
        work_address = "Somewhere Else Avenue"

        



