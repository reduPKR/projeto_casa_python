from django.db import models

# Create your models here.

#define se é agua, energia ou ambos
class TipoConsumo(models.Model):
    nome = models.CharField(max_length=30)

    class Meta:
        db_table = 'tipo_consumo'

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

class MetaTreino(models.Model):
    casa = models.ForeignKey(Casa,on_delete=models.CASCADE)
    mes = models.CharField(max_length=30)

    reduzir_agua_semana = models.FloatField(default=0)
    reduzir_agua_feriado = models.FloatField(default=0)
    
    reduzir_energia_semana = models.FloatField(default=0)
    reduzir_energia_feriado = models.FloatField(default=0)

    class Meta:
        db_table = 'meta_treino'


class ComodoValorY(models.Model):
    comodo = models.ForeignKey(Comodo,on_delete=models.CASCADE)
    meta = models.ForeignKey(MetaTreino, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.IntegerField()

    meta_agua = models.IntegerField(default=0)
    meta_energia = models.IntegerField(default=0)

    class Meta:
        db_table = 'comodo_valor_y'
    
class ComodoEquipamento(models.Model):
    apelido = models.IntegerField()

    comodo = models.ForeignKey(Comodo, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)

    class Meta:
        db_table = 'comodo_equipamento'

class ComodoSaida(models.Model):
    #Apelido é um int que descreve qual é
    #Exemplo tomada 3, uso para que se for excluida e adicionada fique na ordem 1,2,3 ...
    apelido = models.IntegerField()

    comodo = models.ForeignKey(Comodo, on_delete=models.CASCADE)
    saida = models.ForeignKey(Saida, on_delete=models.CASCADE)
    comodo_equipamento = models.ForeignKey(ComodoEquipamento,on_delete=models.CASCADE,null=True)
    essencial = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    
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

#Nao coloquei consumo agua e energia pq da pra ser pego e calculado
class ConsumoMes(models.Model):
    casa = models.ForeignKey(Casa,on_delete=models.CASCADE)
    mes = models.CharField(max_length=30)
    ano = models.IntegerField()
    
    agua = models.IntegerField(default=0)
    agua_semana = models.IntegerField(default=0)
    agua_feriado = models.IntegerField(default=0)

    energia = models.IntegerField(default=0)
    energia_semana = models.IntegerField(default=0)
    energia_feriado = models.IntegerField(default=0)

    class Meta:
        db_table = 'consumo_mes'

class ConsumoHora(models.Model):
    mes = models.ForeignKey(ConsumoMes,on_delete=models.CASCADE)
    comodo_saida = models.ForeignKey(ComodoSaida,on_delete=models.CASCADE)
    tempo = models.IntegerField()
    data = models.DateField()
    hora = models.IntegerField()

    class Meta:
        db_table = 'consumo_hora'

class ConsumoHoraManual(models.Model):
    #Aqui registra a lista de horarios que um equipamento fica ligados
    comodo_saida = models.ForeignKey(ComodoSaida,on_delete=models.CASCADE)
    hora_liga = models.TimeField()
    hora_desliga = models.TimeField()
    semana = models.BooleanField(default=True)

    class Meta:
        db_table = 'consumo_hora_manual'

class Clima(models.Model):
    data = models.DateField()
    hora = models.IntegerField()

    temperatura = models.IntegerField(default=0)
    umidade = models.IntegerField(default=0)
    vento = models.IntegerField(default=0)
    pressao = models.IntegerField(default=0)
    chuva = models.IntegerField(default=0)

    class Meta:
        db_table = 'clima'

class GrupoCoeficiente(models.Model):
    meta_treino = models.ForeignKey(MetaTreino,on_delete=models.CASCADE)
    precisao = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    gerador = models.CharField(max_length=30)

    tempo_treino = models.FloatField(default=0)

    class Meta:
        db_table = 'grupo_coeficientes'

class Coeficiente(models.Model):
    comodo = models.ForeignKey(Comodo, on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoCoeficiente,on_delete=models.CASCADE)
    precisao = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    energia = models.BooleanField(default=True)
    semana = models.BooleanField(default=True)
    
    constante = models.FloatField(default=0)
    temperatura = models.FloatField(default=0)
    umidade = models.FloatField(default=0)
    vento = models.FloatField(default=0)
    pressao = models.FloatField(default=0)
    chuva = models.FloatField(default=0)

    class Meta:
        db_table = 'coeficientes'
