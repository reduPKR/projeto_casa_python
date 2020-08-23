from django.db import models

# Create your models here.

#define se é agua, energia ou ambos
class TipoConsumo(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'tipo_consumo'

#é a categoria, torneira, tomada
class Saida(models.Model):
    tipo_consumo = models.ForeignKey(TipoConsumo,on_delete=models.CASCADE)
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'saida'

#O tipo de quipamento é usado para o algoritmo de regrasao linear
class TipoEquipamento(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'tipo_equipamento'
    
class Equipamento(models.Model):
    tipo_consumo = models.ForeignKey(TipoConsumo,on_delete=models.CASCADE)
    tipo_equipamento = models.ForeignKey(TipoEquipamento,on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=500, null=True)
    consumo_agua = models.FloatField()
    consumo_energia = models.FloatField()

    class Meta:
        db_table = 'equipamento'

class Casa(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'casa'

class Comodo(models.Model):
    casa = models.ForeignKey(Casa,on_delete=models.CASCADE)
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'comodo'

class ComodoSaida(models.Model):
    #Apelido é um int que descreve qual é
    #Exemplo tomada 3, uso para que se for excluida e adicionada fique na ordem 1,2,3 ...
    apelido = models.IntegerField()

    comodo = models.ForeignKey(Comodo, on_delete=models.CASCADE)
    saida = models.ForeignKey(Saida, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, null=True)
    essencial = models.BooleanField(default=False)
    
    tempo_min_semana = models.IntegerField(null=True)
    tempo_max_semana = models.IntegerField(null=True)
    tempo_min_feriado = models.IntegerField(null=True)
    tempo_max_feriado = models.IntegerField(null=True)

    class Meta:
        db_table = 'comodo_saida'

    def get_essencial(self):
        if self.essencial == True:
            return 'Essencial'
        else:
            return 'Não essencial'

class Categoria(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'categoria'

#Nao coloquei consumo agua e energia pq da pra ser pego e calculado
class ConsumoMes(models.Model):
    casa = models.ForeignKey(Casa,on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria,on_delete=models.CASCADE)
    mes = models.DateField()

    class Meta:
        db_table = 'consumo_mes'

class ConsumoHora(models.Model):
    mes = models.ForeignKey(ConsumoMes,on_delete=models.CASCADE)
    comodo_saida = models.ForeignKey(ComodoSaida,on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria,on_delete=models.CASCADE)
    tempo = models.IntegerField()
    data = models.DateField()
    hora = models.IntegerField()
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'consumo_hora'

# class MesHora(models.Model):
#     mes = models.ForeignKey(ConsumoMes,on_delete=models.CASCADE)
#     hora = models.ForeignKey(ConsumoHora,on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'mes_hora'