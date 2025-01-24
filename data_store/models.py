from django.db import models
from pgvector.django import VectorField
from users.models import UserAccount
from pgvector.django import HnswIndex
import uuid

# Create your models here.
class DataStore(models.Model):
    # id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    # company_id = models.ForeignKey(Company, on_delete=models.CASCADE) #.PositiveIntegerField()
    created_by = models.UUIDField(default=uuid.uuid4, editable=False) # models.ForeignKey(UserAccount, on_delete=models.CASCADE)   #.PositiveIntegerField()
    # company_website = models.CharField(max_length=500)
    tokens = models.PositiveIntegerField()
    content = models.TextField("Content", null=False, blank=False)
    embedding = VectorField(
        dimensions=768,
        help_text="Vector embeddings",
        null=True,
        blank=True,
    )
    
    class Meta:
        indexes = [
            HnswIndex(
                name="clip_l14_vectors_index",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]
    
    # def save(self, **kwargs):
    #     data_store = self.model(**kwargs)

    #     data_store.save(using=self._db)