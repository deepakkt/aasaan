from django.db import models
from contacts.models import Zone, Center
from django.contrib.auth.models import User
from smart_selects.db_fields import GroupedForeignKey


class MaterialTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s" % self.name


class ClassTypeMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s" % self.name


class MaterialStatusMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s" % self.name


class ClassMaterialsMaster(models.Model):
    name = models.CharField(max_length=50)
    class_type = models.ForeignKey(ClassTypeMaster, verbose_name='Class Type', on_delete=models.CASCADE)

    def __str__(self):
        return "%s (%s)" % (self.name, self.class_type)

    class Meta:
        verbose_name = 'Class Materials Master'
        ordering = ['name']
        unique_together = ('name', 'class_type')


class CenterMaterialsMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s " % self.name

    class Meta:
        verbose_name = 'Center Materials Master'
        ordering = ['name']


class KitsMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s " % self.name

    class Meta:
        verbose_name = 'Kits Master'
        ordering = ['name']


class OtherMaterialsMaster(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "%s " % self.name

    class Meta:
        verbose_name = 'Other - Event Materials Master'
        ordering = ['name']


class MaterialsRequest(models.Model):
    material_type = models.ForeignKey(MaterialTypeMaster, verbose_name='Material Type', on_delete=models.CASCADE)
    class_type = models.ForeignKey(ClassTypeMaster, verbose_name='Class Type', on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey(MaterialStatusMaster, verbose_name='Status', on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    center = GroupedForeignKey(Center, 'zone', blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    delivery_date = models.DateField('Expected Delivery Date')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = 'NA'
        if self.material_type.pk == 1:
            items = ClassMaterialItem.objects.filter(brochures_request=self).order_by('class_materials')
            if len(items) > 1:
                title = items[0].class_materials.name + ' + '+ str(len(items)-1)
            elif len(items) == 1:
                title = items[0].class_materials.name
        elif self.material_type.pk == 2:
            items = CenterMaterialItem.objects.filter(brochures_request=self).order_by('center_materials')
            if len(items) > 1:
                title = items[0].center_materials.name + ' + '+ str(len(items)-1)
            elif len(items) == 1:
                title = items[0].center_materials.name
        elif self.material_type.pk == 4:
            items = KitsItem.objects.filter(brochures_request=self).order_by('kits')
            if len(items) > 1:
                title = items[0].kits.name + ' + '+ str(len(items)-1)
            elif len(items) == 1:
                title = items[0].kits.name
        else:
            items = OtherMaterialsMasterItem.objects.filter(brochures_request=self).order_by('other_materials')
            if len(items) > 1:
                title = items[0].other_materials.name + ' + '+ str(len(items)-1)
            elif len(items) == 1:
                title = items[0].other_materials.name

        return "%s" % title

    class Meta:
        verbose_name = "Material Request"
        verbose_name_plural = "Materials Request"


class MaterialsRequestIncharge(MaterialsRequest):

    class Meta:
        proxy = True
        verbose_name = 'Materials Incharge'

class ClassMaterialItem(models.Model):
    class_materials = GroupedForeignKey(ClassMaterialsMaster, 'class_type', on_delete=models.CASCADE, blank=True, null=True)
    brochures_request = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', blank=True, null=True)
    sent_quantity = models.IntegerField('Sent Quantity', blank=True, null=True)

    def __str__(self):
        return "%s" % self.class_materials.name

    class Meta:
        verbose_name = 'Class Material'
        verbose_name_plural = 'Class Material'


class CenterMaterialItem(models.Model):
    center_materials = models.ForeignKey(CenterMaterialsMaster, on_delete=models.CASCADE, blank=True, null=True)
    brochures_request = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', blank=True, null=True)
    sent_quantity = models.IntegerField('Sent Quantity', blank=True, null=True)

    def __str__(self):
        return "%s" % self.center_materials.name

    class Meta:
        verbose_name = 'Center Material'
        verbose_name_plural = 'Center Materials'


class KitsItem(models.Model):
    kits = models.ForeignKey(KitsMaster, on_delete=models.CASCADE, blank=True, null=True)
    brochures_request = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', blank=True, null=True)
    sent_quantity = models.IntegerField('Sent Quantity', blank=True, null=True)

    def __str__(self):
        return "%s" % self.kits.name

    class Meta:
        verbose_name = 'Kit'
        verbose_name_plural = 'Kits'


class OtherMaterialsMasterItem(models.Model):
    other_materials = models.ForeignKey(OtherMaterialsMaster, on_delete=models.CASCADE, blank=True, null=True)
    brochures_request = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    quantity = models.IntegerField('quantity', blank=True, null=True)
    sent_quantity = models.IntegerField('Sent Quantity', blank=True, null=True)

    def __str__(self):
        return "%s" % self.other_materials.name

    class Meta:
        verbose_name = 'Other Material Item'
        verbose_name_plural = 'Other Material Items'


class CourierDetails(models.Model):
    accounts_master = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    agency = models.CharField(max_length=100, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    no_of_box = models.SmallIntegerField('No of box', blank=True, null=True)
    sent_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['agency', 'sent_date']
        verbose_name = 'Courier Detail'


class MaterialNotes(models.Model):
    material_request = models.ForeignKey(MaterialsRequest, on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Materials Note'