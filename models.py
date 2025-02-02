from django.db import models

class Material(models.Model):
    sap = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=255)
    quantidade_atual = models.IntegerField(default=0)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sap} - {self.descricao}"

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'

class Movimento(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída')
    ]
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    data = models.DateField()
    rc = models.CharField(max_length=50, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.tipo == 'entrada':
            self.material.quantidade_atual += self.quantidade
        else:  # saída
            if self.material.quantidade_atual >= self.quantidade:
                self.material.quantidade_atual -= self.quantidade
            else:
                raise ValueError("Quantidade insuficiente em estoque")
        
        self.material.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Movimento'
        verbose_name_plural = 'Movimentos'

class ONT(models.Model):
    sap = models.CharField(max_length=50)
    n_doc = models.CharField('Número do Documento', max_length=50)
    carga = models.CharField(max_length=50)
    nome_equipamento = models.CharField('Nome do Equipamento', max_length=255)
    serial = models.CharField('Número de Série', max_length=50, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sap} - {self.serial}"

    class Meta:
        verbose_name = 'ONT'
        verbose_name_plural = 'ONTs'
        ordering = ['-data_cadastro'] 