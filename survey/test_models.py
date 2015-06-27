from django.test import TestCase
import models


class ModeTests(TestCase):

    def test_create_mode(self):
        models.Mode.objects.create(name="bike", met=50.0,
                                   carb=0.0, speed=20.0, green=True)
        bike = models.Mode.objects.get(name='bike')
        self.assertEqual(bike.name, 'bike')
        self.assertEqual(bike.speed, 20.0)
        self.assertEqual(bike.carb, 0.0)
        self.assertEqual(bike.met, 50.0)
        self.assertEqual(bike.green, True)




class EmployerTests(TestCase):
    def test_create_employer(self):
        models.Employer.objects.create(name="Co.Inc.", nr_employees=5000,
                                       active2015=True)
        employer = models.Employer.objects.get(name="Co.Inc.")
        self.assertEqual(employer.name, "Co.Inc.")
        self.assertEqual(employer.nr_employees, 5000)
        self.assertTrue(employer.active2015)








