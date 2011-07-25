from django.db import models
from facilities.models import *

class FacilityTable(models.Model):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    
    @property
    def display_dict(self):
        variables = list(self.variables.all())
        column_variables = [v.display_dict for v in variables]
        return {
            'name': self.name,
            'slug': self.slug,
            'columns': column_variables,
            'subgroups': [{'name': s.name,
                'slug': s.slug} for s in self.subgroups.all()]
        }
    
    def add_column(self, data):
        ColumnCategory.objects.get_or_create(table=self, slug=data['slug'], name=data['name'])
    
    def add_variable(self, variable_data):
        variable_data['facility_table'] = self
        TableColumn.objects.get_or_create(**variable_data)

class TableColumn(models.Model):
    #there's a lot of overlap with facilities.Variable, but there's view-specific stuff
    #that needs a home.
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    description = models.TextField(null=True)
    clickable = models.BooleanField(default=False)
    click_action = models.CharField(max_length=64, null=True)
    subgroups = models.CharField(max_length=512, null=True)
    variable_id = models.IntegerField(null=True)
    facility_table = models.ForeignKey(FacilityTable, related_name="variables")
    #display specific details
    display_style = models.CharField(max_length=64, null=True)
    #calc specific info
    calc_action = models.CharField(max_length=256, null=True)
    calc_columns = models.CharField(max_length=512, null=True)
    iconify_png_url = models.CharField(max_length=256, null=True)
    display_order = models.IntegerField()
    
    @property
    def display_dict(self):
        #this stuff is an extra step. I was hoping this extra step would lead
        # to more flexibility (e.g. in turning 'click_action' from a string into a list.)
        #Down the line, I definitely want to change how this is done. [-AD]
        subgroups = []
        if not self.subgroups == "":
            subgroups = self.subgroups.split(" ")
        d = {
            'name': self.name,
            'slug': self.slug,
            'subgroups': subgroups,
            'clickable': self.clickable,
            'display_order': self.display_order
        }
        if not self.iconify_png_url in ['', None]:
            d['iconify_png_url'] = self.iconify_png_url
        if not self.click_action == '':
            d['click_actions'] = self.click_action.split(' ')
        if not self.display_style in [None, '']:
            d['display_style'] = self.display_style
        
        if not self.calc_action in [None, '']:
            d['calc_action'] = self.calc_action
            d['calc_columns'] = self.calc_columns
        
        if not self.description in [None, '']:
            d['description'] = self.description
        return d

class ColumnCategory(models.Model):
    name = models.CharField(max_length=64)
    slug = models.CharField(max_length=64)
    table = models.ForeignKey(FacilityTable, related_name='subgroups')

class MapLayerDescription(models.Model):
    slug = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    data_source = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    display_order = models.PositiveSmallIntegerField()
    sector_string = models.CharField(max_length=64)

