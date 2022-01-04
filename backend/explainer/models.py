from django.db import models


class NetworkSpec(models.Model):
    """
    Django model for the json network graph spec for one patient
    """
    patient = models.CharField(max_length=100, unique=True, null=True)
    spec = models.JSONField()

    def __str__(self):
        return self.spec


# TODO: More abstracted network model
# class Node(models.Model):
#     """
#     Django model for one node in the network graph
#     """
#     name = models.CharField(max_length=100, unique=True)
#     group = models.CharField(max_length=100)
#     order = models.IntegerField()

#     def __str__(self):
#         return self.name


# class Link(models.Model):
#     """
#     Django model for one link in the network graph
#     """
#     # source and target nodes
#     source = models.ForeignKey(
#         Node, on_delete=models.CASCADE, related_name="from+"
#     )
#     target = models.ForeignKey(
#         Node, on_delete=models.CASCADE, related_name="to"
#     )

#     # certainty and strentgh of the links
#     certainty = models.FloatField(
#         validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
#     )
#     strength = models.FloatField(
#         validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
#     )

#     def __str__(self):
#         return f"Link from {self.source} to {self.target}."


# class Network(models.Model):
#     """
#     Django model for the network
#     """
#     nodes = models.ManyToManyField(Node)
#     links = models.ManyToManyField(Link)

#     def serialize(self):
#         return serializers.serialize("json", self.objects.all())
