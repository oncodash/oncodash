from django.db import models


class Effect(models.Model):
    cui = models.CharField(max_length=7)  # Side effect id
    name = models.TextField()  # Side effect name

    class Meta:
        constraints = [models.UniqueConstraint(fields=["cui"], name='unique_cui')]


class Interaction(models.Model):
    drug_a = models.ForeignKey('Drug', related_name='drugs_a', on_delete=models.CASCADE)
    drug_b = models.ForeignKey('Drug', related_name='drugs_b', on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)


class Drug(models.Model):
    title = models.TextField()  # Name of the drug
    description = models.TextField(blank=True, null=True)  # Textual description of the drug
    description_url = models.TextField(blank=True, null=True)  # Source of the "description" field
    cid = models.CharField(max_length=9)  # Identifier from database of chemical molecules and their activities in
                                           # biological assays (Compound ID number)
    molecular_formula = models.TextField(blank=True, null=True)  # Molecular formula of the drug
    effects = models.ManyToManyField(Effect)  # Possible side-effects of the drug
    interactions = models.ManyToManyField('Drug', through=Interaction, blank=True, through_fields= ('drug_a', 'drug_b'))

    class Meta:
        constraints = [models.UniqueConstraint(fields=["cid"], name='unique_cid')]