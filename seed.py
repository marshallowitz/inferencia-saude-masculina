import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
import random

DB_PATH = 'health.db'

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

# ── Seed data ──────────────────────────────────────────────────────

DOCTOR = {
    'name': 'Sofia Marshallowitz',
    'email': 'sofia@saude.med.br',
    'password': 'sofia123',
    'role': 'doctor',
}

PATIENTS = [
    {
        'name': 'Carlos Eduardo Nunes',
        'email': 'carlos.nunes@email.com',
        'password': 'paciente123',
        'role': 'patient',
    },
    {
        'name': 'Roberto Alves',
        'email': 'roberto.alves@email.com',
        'password': 'paciente123',
        'role': 'patient',
    },
    {
        'name': 'Marcos Ferreira',
        'email': 'marcos.ferreira@email.com',
        'password': 'paciente123',
        'role': 'patient',
    },
    {
        'name': 'José Henrique Lima',
        'email': 'jose.lima@email.com',
        'password': 'paciente123',
        'role': 'patient',
    },
    {
        'name': 'André Cavalcante',
        'email': 'andre.cavalcante@email.com',
        'password': 'paciente123',
        'role': 'patient',
    },
]

# Records per patient: list of (input_data, days_ago)
# Each input_data maps dado_id -> {idx, alpha, risco}
PATIENT_RECORDS = [
    # Carlos Eduardo Nunes — 47 anos, síndrome metabólica + risco DM2 elevado
    [
        {
            'days_ago': 180,
            'notes': 'Primeira consulta. Sobrepeso significativo, glicemia limítrofe.',
            'input': {
                'imc':         {'idx': 2, 'alpha': 1.0, 'risco': True},
                'cintura':     {'idx': 2, 'alpha': 1.0, 'risco': True},
                'glicemia':    {'idx': 1, 'alpha': 0.8, 'risco': True},
                'hba1c':       {'idx': 1, 'alpha': 0.8, 'risco': True},
                'triglicerides': {'idx': 1, 'alpha': 0.7, 'risco': True},
                'hdl':         {'idx': 2, 'alpha': 1.0, 'risco': True},
                'pressao':     {'idx': 2, 'alpha': 0.8, 'risco': True},
                'phq9':        {'idx': 1, 'alpha': 0.7, 'risco': True},
                'sono_horas':  {'idx': 2, 'alpha': 1.0, 'risco': True},
                'atv_fisica':  {'idx': 2, 'alpha': 1.0, 'risco': True},
                'idade':       {'idx': 1, 'alpha': 0.5, 'risco': True},
                'hist_familiar_dm': {'idx': 2, 'alpha': 1.0, 'risco': True},
            },
        },
        {
            'days_ago': 90,
            'notes': 'Retorno 6 meses. Perdeu 4 kg. Glicemia melhorou.',
            'input': {
                'imc':         {'idx': 2, 'alpha': 1.0, 'risco': True},
                'cintura':     {'idx': 1, 'alpha': 0.7, 'risco': True},
                'glicemia':    {'idx': 0, 'alpha': 0.3, 'risco': False},
                'hba1c':       {'idx': 1, 'alpha': 0.8, 'risco': True},
                'triglicerides': {'idx': 1, 'alpha': 0.7, 'risco': True},
                'hdl':         {'idx': 2, 'alpha': 1.0, 'risco': True},
                'pressao':     {'idx': 1, 'alpha': 0.3, 'risco': False},
                'phq9':        {'idx': 1, 'alpha': 0.7, 'risco': True},
                'sono_horas':  {'idx': 1, 'alpha': 0.7, 'risco': True},
                'atv_fisica':  {'idx': 1, 'alpha': 0.6, 'risco': True},
                'idade':       {'idx': 1, 'alpha': 0.5, 'risco': True},
                'hist_familiar_dm': {'idx': 2, 'alpha': 1.0, 'risco': True},
            },
        },
        {
            'days_ago': 7,
            'notes': 'Retorno 3 meses. Progresso mantido. Iniciando metformina.',
            'input': {
                'imc':         {'idx': 1, 'alpha': 0.6, 'risco': True},
                'cintura':     {'idx': 1, 'alpha': 0.7, 'risco': True},
                'glicemia':    {'idx': 0, 'alpha': 0.3, 'risco': False},
                'hba1c':       {'idx': 0, 'alpha': 0.3, 'risco': False},
                'triglicerides': {'idx': 0, 'alpha': 0.3, 'risco': False},
                'hdl':         {'idx': 1, 'alpha': 0.3, 'risco': False},
                'pressao':     {'idx': 1, 'alpha': 0.3, 'risco': False},
                'phq9':        {'idx': 0, 'alpha': 0.3, 'risco': False},
                'sono_horas':  {'idx': 0, 'alpha': 0.3, 'risco': False},
                'atv_fisica':  {'idx': 1, 'alpha': 0.6, 'risco': True},
                'idade':       {'idx': 1, 'alpha': 0.5, 'risco': True},
                'hist_familiar_dm': {'idx': 2, 'alpha': 1.0, 'risco': True},
            },
        },
    ],
    # Roberto Alves — 55 anos, risco cardiovascular + tabagismo
    [
        {
            'days_ago': 120,
            'notes': 'Fumante há 20 anos. Hipertensão estágio 2. Encaminhado por cardiologista.',
            'input': {
                'imc':          {'idx': 1, 'alpha': 0.6, 'risco': True},
                'pressao':      {'idx': 3, 'alpha': 1.0, 'risco': True},
                'tabagismo':    {'idx': 3, 'alpha': 1.0, 'risco': True},
                'colesterol':   {'idx': 2, 'alpha': 1.0, 'risco': True},
                'triglicerides':{'idx': 2, 'alpha': 1.0, 'risco': True},
                'hdl':          {'idx': 2, 'alpha': 1.0, 'risco': True},
                'glicemia':     {'idx': 1, 'alpha': 0.8, 'risco': True},
                'medic_antihiper': {'idx': 2, 'alpha': 1.0, 'risco': True},
                'idade':        {'idx': 2, 'alpha': 0.8, 'risco': True},
                'hist_familiar_cv': {'idx': 2, 'alpha': 1.0, 'risco': True},
                'atv_fisica':   {'idx': 2, 'alpha': 1.0, 'risco': True},
                'phq9':         {'idx': 1, 'alpha': 0.7, 'risco': True},
                'psa':          {'idx': 1, 'alpha': 0.6, 'risco': True},
                'pcr_alta':     {'idx': 2, 'alpha': 1.0, 'risco': True},
            },
        },
        {
            'days_ago': 30,
            'notes': 'Retorno 3 meses. Parou de fumar. PA ainda alta mas melhorando.',
            'input': {
                'imc':          {'idx': 1, 'alpha': 0.6, 'risco': True},
                'pressao':      {'idx': 2, 'alpha': 0.8, 'risco': True},
                'tabagismo':    {'idx': 2, 'alpha': 0.7, 'risco': True},
                'colesterol':   {'idx': 1, 'alpha': 0.7, 'risco': True},
                'triglicerides':{'idx': 1, 'alpha': 0.7, 'risco': True},
                'hdl':          {'idx': 1, 'alpha': 0.3, 'risco': False},
                'glicemia':     {'idx': 0, 'alpha': 0.3, 'risco': False},
                'medic_antihiper': {'idx': 1, 'alpha': 0.6, 'risco': True},
                'idade':        {'idx': 2, 'alpha': 0.8, 'risco': True},
                'hist_familiar_cv': {'idx': 2, 'alpha': 1.0, 'risco': True},
                'atv_fisica':   {'idx': 1, 'alpha': 0.6, 'risco': True},
                'pcr_alta':     {'idx': 1, 'alpha': 0.5, 'risco': True},
            },
        },
    ],
    # Marcos Ferreira — 38 anos, saúde mental + burnout
    [
        {
            'days_ago': 60,
            'notes': 'PHQ-9 = 12. GAD-7 = 14. Trabalha 14h/dia. Wearable mostra HRV muito reduzida.',
            'input': {
                'phq9':             {'idx': 2, 'alpha': 0.9, 'risco': True},
                'phq2':             {'idx': 2, 'alpha': 1.0, 'risco': True},
                'gad7':             {'idx': 2, 'alpha': 0.9, 'risco': True},
                'estresse_percebido': {'idx': 2, 'alpha': 1.0, 'risco': True},
                'diag_mental':      {'idx': 1, 'alpha': 0.8, 'risco': True},
                'hrv':              {'idx': 2, 'alpha': 1.0, 'risco': True},
                'sono_wearable':    {'idx': 2, 'alpha': 1.0, 'risco': True},
                'sono_horas':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'uso_noturno':      {'idx': 2, 'alpha': 1.0, 'risco': True},
                'passos_dia':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'atv_fisica':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'qualidade_vida':   {'idx': 1, 'alpha': 0.8, 'risco': True},
                'funcao_sexual':    {'idx': 1, 'alpha': 0.7, 'risco': True},
                'suporte_social':   {'idx': 1, 'alpha': 0.7, 'risco': True},
                'idade':            {'idx': 0, 'alpha': 0.2, 'risco': False},
            },
        },
        {
            'days_ago': 14,
            'notes': 'Retorno 6 semanas. Iniciou ISRS. Afastamento do trabalho por 30 dias.',
            'input': {
                'phq9':             {'idx': 1, 'alpha': 0.7, 'risco': True},
                'phq2':             {'idx': 1, 'alpha': 0.8, 'risco': True},
                'gad7':             {'idx': 1, 'alpha': 0.7, 'risco': True},
                'estresse_percebido': {'idx': 1, 'alpha': 0.7, 'risco': True},
                'diag_mental':      {'idx': 2, 'alpha': 0.9, 'risco': True},
                'medic_psiq':       {'idx': 1, 'alpha': 0.6, 'risco': True},
                'hrv':              {'idx': 1, 'alpha': 0.7, 'risco': True},
                'sono_wearable':    {'idx': 1, 'alpha': 0.7, 'risco': True},
                'sono_horas':       {'idx': 1, 'alpha': 0.7, 'risco': True},
                'uso_noturno':      {'idx': 1, 'alpha': 0.8, 'risco': True},
                'passos_dia':       {'idx': 1, 'alpha': 0.5, 'risco': True},
                'qualidade_vida':   {'idx': 1, 'alpha': 0.8, 'risco': True},
            },
        },
    ],
    # José Henrique Lima — 62 anos, rastreamento oncológico + próstata
    [
        {
            'days_ago': 45,
            'notes': 'PSA 4,8 ng/mL. Toque retal alterado. Encaminhado para urologista.',
            'input': {
                'psa':              {'idx': 2, 'alpha': 0.9, 'risco': True},
                'psa_livre':        {'idx': 1, 'alpha': 0.6, 'risco': True},
                'dre':              {'idx': 1, 'alpha': 1.0, 'risco': True},
                'sint_urinarios':   {'idx': 1, 'alpha': 0.7, 'risco': True},
                'hist_familiar_prostata': {'idx': 1, 'alpha': 0.8, 'risco': True},
                'idade':            {'idx': 3, 'alpha': 1.0, 'risco': True},
                'imc':              {'idx': 2, 'alpha': 1.0, 'risco': True},
                'hist_familiar_crc': {'idx': 1, 'alpha': 0.6, 'risco': True},
                'dieta_vermelha':   {'idx': 2, 'alpha': 1.0, 'risco': True},
                'atv_fisica':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'alcool':           {'idx': 1, 'alpha': 0.6, 'risco': True},
                'pcr_alta':         {'idx': 2, 'alpha': 1.0, 'risco': True},
                'igf1':             {'idx': 1, 'alpha': 0.7, 'risco': True},
                'insulina':         {'idx': 1, 'alpha': 0.7, 'risco': True},
                'glicemia':         {'idx': 1, 'alpha': 0.8, 'risco': True},
                'diabetes':         {'idx': 2, 'alpha': 0.8, 'risco': True},
            },
        },
    ],
    # André Cavalcante — 44 anos, obesidade + apneia + elegibilidade GLP-1
    [
        {
            'days_ago': 30,
            'notes': 'IMC 38. Apneia grave confirmada. Candidato a GLP-1. Sem contraindicações.',
            'input': {
                'imc':              {'idx': 3, 'alpha': 1.0, 'risco': True},
                'cintura':          {'idx': 2, 'alpha': 1.0, 'risco': True},
                'peso_desejado':    {'idx': 2, 'alpha': 1.0, 'risco': True},
                'variacao_peso':    {'idx': 1, 'alpha': 0.8, 'risco': True},
                'apneia':           {'idx': 3, 'alpha': 1.0, 'risco': True},
                'sono_qualidade':   {'idx': 2, 'alpha': 0.9, 'risco': True},
                'sono_horas':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'sonolencia':       {'idx': 1, 'alpha': 0.8, 'risco': True},
                'glicemia':         {'idx': 1, 'alpha': 0.8, 'risco': True},
                'hba1c':            {'idx': 1, 'alpha': 0.8, 'risco': True},
                'triglicerides':    {'idx': 2, 'alpha': 1.0, 'risco': True},
                'hdl':              {'idx': 2, 'alpha': 1.0, 'risco': True},
                'pressao':          {'idx': 2, 'alpha': 0.8, 'risco': True},
                'atv_fisica':       {'idx': 2, 'alpha': 1.0, 'risco': True},
                'sedentarismo':     {'idx': 2, 'alpha': 1.0, 'risco': True},
                'dieta':            {'idx': 2, 'alpha': 1.0, 'risco': True},
                'gi_gastroparesia': {'idx': 0, 'alpha': 0.1, 'risco': False},
                'glp1_historico':   {'idx': 0, 'alpha': 0.3, 'risco': False},
                'phq9':             {'idx': 1, 'alpha': 0.7, 'risco': True},
                'idade':            {'idx': 1, 'alpha': 0.5, 'risco': True},
            },
        },
    ],
]

# Simple engine to compute results from input_data
# (mirrors the JS logic from app.html)

N1_DEFS = [
    {'id':'n1_obesidade','nome':'Obesidade e perfil adiposo','nivel':'N1','dominio':'Metabolismo','ref':'ABESO 2022; IDF 2006','alertMental':False,
     'vars':[('imc',35),('cintura',25),('peso_desejado',15),('atv_fisica',15),('variacao_peso',10)]},
    {'id':'n1_dm2','nome':'Risco de diabetes tipo 2 (FINDRISC)','nivel':'N1','dominio':'Metabolismo','ref':'Lindström & Tuomilehto 2003; AUC=0,76','alertMental':False,
     'vars':[('hist_glicemia',25),('hist_familiar_dm',19),('imc',18),('atv_fisica',15),('medic_antihiper',12),('idade',11)]},
    {'id':'n1_cardio','nome':'Risco cardiovascular (Framingham)','nivel':'N1','dominio':'Cardiovascular','ref':"D'Agostino 2008; AUC=0,794",'alertMental':False,
     'vars':[('pressao',28),('colesterol',22),('tabagismo',14),('diabetes',14),('idade',14),('medic_antihiper',8)]},
    {'id':'n1_sindrome_met_vars','nome':'Componentes da síndrome metabólica','nivel':'N1','dominio':'Metabolismo','ref':'Alberti et al. 2009','alertMental':False,
     'vars':[('cintura',22),('triglicerides',20),('hdl',20),('pressao',20),('glicemia',18)]},
    {'id':'n1_resistencia_insulinica','nome':'Resistência insulínica / hiperinsulinemia','nivel':'N1','dominio':'Metabolismo','ref':'Matthews 1985 (HOMA-IR)','alertMental':False,
     'vars':[('insulina',35),('hba1c',25),('glicemia',18),('imc',12),('igf1',10)]},
    {'id':'n1_inflamacao_cronica','nome':'Inflamação crônica de baixo grau','nivel':'N1','dominio':'Metabolismo','ref':'ERFC 2010 JAMA','alertMental':False,
     'vars':[('pcr_alta',35),('imc',22),('cintura',18),('adiponectina',15),('leucocitos',10)]},
    {'id':'n1_depressao','nome':'Triagem de depressão (PHQ-2/9)','nivel':'N1','dominio':'Saúde mental','ref':'Kroenke & Spitzer 2001; AUC=0,95','alertMental':True,
     'vars':[('phq9',45),('phq2',25),('diag_mental',20),('medic_psiq',10)]},
    {'id':'n1_ansiedade','nome':'Triagem de ansiedade (GAD-7)','nivel':'N1','dominio':'Saúde mental','ref':'Spitzer 2006; AUC=0,91','alertMental':True,
     'vars':[('gad7',60),('estresse_percebido',25),('diag_mental',15)]},
    {'id':'n1_sono','nome':'Qualidade do sono e apneia','nivel':'N1','dominio':'Sono','ref':'AASM 2015; ISI AUC=0,87','alertMental':False,
     'vars':[('apneia',30),('sono_qualidade',28),('sono_horas',22),('sonolencia',12),('ritmo_circadiano',8)]},
    {'id':'n1_elegib_glp1','nome':'Elegibilidade farmacológica (GLP-1)','nivel':'N1','dominio':'Farmacologia','ref':'FDA 2021/2022; STEP 1','alertMental':False,
     'vars':[('imc',30),('gi_gastroparesia',25),('hist_familiar_prostata',15),('diag_mental',15),('glp1_historico',15)]},
    {'id':'n1_prostata','nome':'Risco de câncer de próstata','nivel':'N1','dominio':'Oncologia','ref':'Ross 2007; AUC=0,766','alertMental':False,
     'vars':[('psa',35),('psa_livre',20),('idade',18),('hist_familiar_prostata',15),('dre',7),('sint_urinarios',5)]},
    {'id':'n1_cancer_crc','nome':'Risco de câncer colorretal (LiFeCRC)','nivel':'N1','dominio':'Oncologia','ref':'LiFeCRC AUC=0,77','alertMental':False,
     'vars':[('idade',28),('hist_familiar_crc',20),('imc',15),('alcool',12),('tabagismo',10),('dieta_vermelha',8),('atv_fisica',5),('sangue_fezes',2)]},
    {'id':'n1_distress_onco','nome':'Distress oncológico (NCCN DT)','nivel':'N1','dominio':'Saúde mental','ref':'Mitchell 2007','alertMental':True,
     'vars':[('distress_onco',40),('phq9',25),('medo_recorrencia',20),('suporte_social',15)]},
    {'id':'n1_qualidade_vida','nome':'Qualidade de vida (SF-12/36)','nivel':'N1','dominio':'Bem-estar','ref':'Kolotkin 2017','alertMental':False,
     'vars':[('qualidade_vida',45),('funcao_sexual',25),('sono_qualidade',15),('atv_fisica',10),('estresse_percebido',5)]},
    {'id':'n1_hiperinsulinemia_cancer','nome':'Hiperinsulinemia e risco oncológico','nivel':'N1','dominio':'Oncologia','ref':'IARC 2024','alertMental':False,
     'vars':[('imc',22),('insulina',20),('glicemia',18),('pcr_alta',15),('triglicerides',12),('igf1',8),('adiponectina',5)]},
    {'id':'n1_burnout','nome':'Burnout ocupacional (fenotipagem)','nivel':'N1','dominio':'Saúde mental','ref':'Barac 2024 JMIR','alertMental':True,
     'vars':[('hrv',35),('sono_wearable',25),('passos_dia',15),('uso_noturno',12),('ritmo_circadiano',8)]},
]

N2_DEFS = [
    {'id':'n2_sindrome_met','nome':'Síndrome metabólica integrada','nivel':'N2','dominio':'Metabolismo','ref':'Alberti 2009','alertMental':False,
     'needs':['n1_cardio','n1_dm2','n1_sindrome_met_vars','n1_obesidade'],
     'pesos':{'n1_cardio':0.30,'n1_dm2':0.28,'n1_sindrome_met_vars':0.25,'n1_obesidade':0.17},'min':2},
    {'id':'n2_saude_mental_peso','nome':'Saúde mental e emagrecimento','nivel':'N2','dominio':'Psicossomático','ref':'Luppino 2010','alertMental':True,
     'needs':['n1_depressao','n1_obesidade','n1_sono','n1_ansiedade'],
     'pesos':{'n1_depressao':0.35,'n1_obesidade':0.30,'n1_sono':0.20,'n1_ansiedade':0.15},'min':2},
    {'id':'n2_risco_cardiomet','nome':'Risco cardiometabólico integrado','nivel':'N2','dominio':'Cardiovascular','ref':'GBD 2019','alertMental':False,
     'needs':['n1_cardio','n2_sindrome_met','n1_dm2'],
     'pesos':{'n1_cardio':0.40,'n2_sindrome_met':0.35,'n1_dm2':0.25},'min':2},
    {'id':'n2_elegib_completa','nome':'Elegibilidade integrada para GLP-1','nivel':'N2','dominio':'Farmacologia','ref':'STEP 1','alertMental':False,
     'needs':['n1_elegib_glp1','n1_obesidade','n1_depressao','n1_sono'],
     'pesos':{'n1_elegib_glp1':0.40,'n1_obesidade':0.35,'n1_depressao':0.15,'n1_sono':0.10},'min':2},
    {'id':'n2_sono_mental','nome':'Sono e saúde mental integrados','nivel':'N2','dominio':'Psicossomático','ref':'Baglioni 2016','alertMental':True,
     'needs':['n1_depressao','n1_sono','n1_ansiedade','n1_burnout'],
     'pesos':{'n1_depressao':0.35,'n1_sono':0.30,'n1_ansiedade':0.20,'n1_burnout':0.15},'min':2},
    {'id':'n2_obesidade_cancer','nome':'Obesidade metabólica e risco oncológico','nivel':'N2','dominio':'Oncologia','ref':'IARC 2024','alertMental':False,
     'needs':['n1_hiperinsulinemia_cancer','n1_inflamacao_cronica','n1_sindrome_met_vars','n1_obesidade'],
     'pesos':{'n1_hiperinsulinemia_cancer':0.35,'n1_inflamacao_cronica':0.30,'n1_sindrome_met_vars':0.20,'n1_obesidade':0.15},'min':2},
    {'id':'n2_depressao_cancer','nome':'Depressão, ansiedade e prognóstico oncológico','nivel':'N2','dominio':'Psico-oncologia','ref':'van Tuijl 2023','alertMental':True,
     'needs':['n1_distress_onco','n1_depressao','n1_ansiedade','n1_qualidade_vida'],
     'pesos':{'n1_distress_onco':0.35,'n1_depressao':0.30,'n1_ansiedade':0.20,'n1_qualidade_vida':0.15},'min':2},
    {'id':'n2_cancer_crc_integrado','nome':'Risco integrado de câncer colorretal','nivel':'N2','dominio':'Oncologia','ref':'LiFeCRC AUC=0,77','alertMental':False,
     'needs':['n1_cancer_crc','n1_hiperinsulinemia_cancer','n1_inflamacao_cronica','n2_sindrome_met'],
     'pesos':{'n1_cancer_crc':0.40,'n1_hiperinsulinemia_cancer':0.25,'n1_inflamacao_cronica':0.20,'n2_sindrome_met':0.15},'min':2},
    {'id':'n2_psicossomatico_integrado','nome':'Saúde psicossomática integrada','nivel':'N2','dominio':'Psicossomático','ref':'Lancet Psychiatry 2025','alertMental':True,
     'needs':['n2_saude_mental_peso','n2_sono_mental','n1_qualidade_vida','n1_inflamacao_cronica'],
     'pesos':{'n2_saude_mental_peso':0.40,'n2_sono_mental':0.25,'n1_qualidade_vida':0.20,'n1_inflamacao_cronica':0.15},'min':2},
]

N3_DEFS = [
    {'id':'n3_saude_masc_360','nome':'Perfil de saúde masculina 360°','nivel':'N3','dominio':'Meta-inferência','ref':'WHO NCD Action Plan 2030','alertMental':False,
     'needs':['n2_sindrome_met','n2_saude_mental_peso','n2_risco_cardiomet','n2_elegib_completa','n2_sono_mental'],
     'pesos':{'n2_sindrome_met':0.28,'n2_saude_mental_peso':0.25,'n2_risco_cardiomet':0.22,'n2_elegib_completa':0.15,'n2_sono_mental':0.10},'min':2},
    {'id':'n3_risco_oncologico_integrado','nome':'Risco oncológico integrado','nivel':'N3','dominio':'Oncologia / Meta-inferência','ref':'IARC 2020','alertMental':False,
     'needs':['n2_obesidade_cancer','n2_cancer_crc_integrado','n1_prostata','n1_hiperinsulinemia_cancer','n2_depressao_cancer'],
     'pesos':{'n2_obesidade_cancer':0.30,'n2_cancer_crc_integrado':0.28,'n1_prostata':0.20,'n1_hiperinsulinemia_cancer':0.14,'n2_depressao_cancer':0.08},'min':2},
    {'id':'n3_carga_doenca_mental_metabolica','nome':'Carga de doença mental-metabólica integrada','nivel':'N3','dominio':'Psicossomático / Meta-inferência','ref':'GBD 2019','alertMental':True,
     'needs':['n2_psicossomatico_integrado','n2_sindrome_met','n2_sono_mental','n1_qualidade_vida','n2_elegib_completa'],
     'pesos':{'n2_psicossomatico_integrado':0.32,'n2_sindrome_met':0.25,'n2_sono_mental':0.18,'n1_qualidade_vida':0.15,'n2_elegib_completa':0.10},'min':3},
    {'id':'n3_viabilidade_terapeutica','nome':'Viabilidade terapêutica global','nivel':'N3','dominio':'Meta-inferência','ref':'Look AHEAD NEJM 2012','alertMental':False,
     'needs':['n2_elegib_completa','n2_risco_cardiomet','n2_sindrome_met','n1_sono','n1_qualidade_vida'],
     'pesos':{'n2_elegib_completa':0.35,'n2_risco_cardiomet':0.25,'n2_sindrome_met':0.20,'n1_sono':0.12,'n1_qualidade_vida':0.08},'min':2},
]


def calc_cov(var_list, input_data):
    sum_w = sum_wa = 0
    for vid, p in var_list:
        sum_w += p
        st = input_data.get(vid)
        if st:
            sum_wa += p * st['alpha']
    if not sum_w:
        return 0.0, 0
    informed = sum(1 for vid, _ in var_list if vid in input_data)
    return sum_wa / sum_w, informed


def run_engine(input_data):
    n1_r = {}
    for m in N1_DEFS:
        cov, informed = calc_cov(m['vars'], input_data)
        n1_r[m['id']] = {'cov': cov, 'informed': informed, 'active': cov > 0.05 and informed >= 1, **m}

    n2_r = {}
    for m in N2_DEFS:
        ready = [nid for nid in m['needs'] if n1_r.get(nid, {}).get('active')]
        if len(ready) < m.get('min', 1):
            n2_r[m['id']] = {'cov': 0, 'informed': 0, 'active': False, **m}
            continue
        sw = swa = 0
        for nid in m['needs']:
            w = m['pesos'].get(nid, 0)
            sw += w
            if n1_r.get(nid, {}).get('active'):
                swa += w * n1_r[nid]['cov']
        cov = swa / sw if sw else 0
        n2_r[m['id']] = {'cov': cov, 'informed': len(ready), 'active': cov > 0.05, **m}

    all_r = {**n1_r, **n2_r}
    n3_r = {}
    for m in N3_DEFS:
        ready = [nid for nid in m['needs'] if all_r.get(nid, {}).get('active')]
        if len(ready) < m.get('min', 1):
            n3_r[m['id']] = {'cov': 0, 'informed': 0, 'active': False, **m}
            continue
        sw = swa = 0
        for nid in m['needs']:
            w = m['pesos'].get(nid, 0)
            sw += w
            if all_r.get(nid, {}).get('active'):
                swa += w * all_r[nid]['cov']
        cov = swa / sw if sw else 0
        n3_r[m['id']] = {'cov': cov, 'informed': len(ready), 'active': cov > 0.05, **m}

    results = []
    for m_list in [N1_DEFS, N2_DEFS, N3_DEFS]:
        lookup = {**n1_r, **n2_r, **n3_r}
        for m in m_list:
            r = lookup.get(m['id'])
            if r and r.get('active'):
                results.append({
                    'id': m['id'],
                    'nivel': m['nivel'],
                    'nome': m['nome'],
                    'dominio': m['dominio'],
                    'ref': m['ref'],
                    'alertMental': m['alertMental'],
                    'cov': r['cov'],
                })
    results.sort(key=lambda x: -x['cov'])
    return results


def ts_offset(days_ago):
    dt = datetime.utcnow() - timedelta(days=days_ago)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def upsert_user(conn, u):
    existing = conn.execute('SELECT id FROM users WHERE email=?', (u['email'],)).fetchone()
    if existing:
        print(f"  [skip] Usuário já existe: {u['email']}")
        return existing['id']
    conn.execute(
        'INSERT INTO users (name,email,password_hash,role,created_at) VALUES (?,?,?,?,?)',
        (u['name'], u['email'], hash_pw(u['password']), u['role'], ts_offset(365))
    )
    uid = conn.execute('SELECT id FROM users WHERE email=?', (u['email'],)).fetchone()['id']
    print(f"  [+] Criado: {u['name']} ({u['role']}) — {u['email']}")
    return uid


def seed():
    conn = get_db()

    print('\n=== Criando médica ===')
    doc_id = upsert_user(conn, DOCTOR)

    print('\n=== Criando pacientes e registros ===')
    for i, (pat, records) in enumerate(zip(PATIENTS, PATIENT_RECORDS)):
        pat_id = upsert_user(conn, pat)

        # Link doctor <-> patient
        conn.execute(
            'INSERT OR IGNORE INTO doctor_patients VALUES (?,?)', (doc_id, pat_id)
        )

        # Check existing records for this patient
        existing_count = conn.execute(
            'SELECT COUNT(*) as c FROM records WHERE patient_id=?', (pat_id,)
        ).fetchone()['c']

        if existing_count > 0:
            print(f"  [skip] {pat['name']} já tem {existing_count} registro(s)")
            continue

        for rec in records:
            input_data = rec['input']
            results = run_engine(input_data)
            conn.execute(
                'INSERT INTO records (patient_id,doctor_id,input_data,results,notes,created_at) VALUES (?,?,?,?,?,?)',
                (pat_id, doc_id, json.dumps(input_data), json.dumps(results), rec['notes'], ts_offset(rec['days_ago']))
            )
            print(f"    → Registro criado: {pat['name']} ({rec['days_ago']}d atrás) — {len(results)} inferências")

    conn.commit()
    conn.close()

    print('\n=== Seed concluído ===')
    print(f'\nAcesse como médica:')
    print(f'  E-mail: {DOCTOR["email"]}')
    print(f'  Senha:  {DOCTOR["password"]}')
    print(f'\nSenha de todos os pacientes: paciente123')
    for p in PATIENTS:
        print(f'  {p["name"]} — {p["email"]}')


if __name__ == '__main__':
    seed()
