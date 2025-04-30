# =============================================================================
# Autor: Giovanni Leopoldo Rozza - Jan. 2020
# Arquivo com as constantes globais de configuração dos setups e
# conexao MT5
# =============================================================================

#######################################################################
# CONFIGURACAOES GERAIS
#######################################################################
import datetime
import pytz

MT5_TIMEFAME_M60  =1
MT5_TIMEFAME_M2  =2
MT5_TIMEFAME_M3  =3
MT5_TIMEFAME_M4  =4
MT5_TIMEFAME_M5  =5
MT5_TIMEFAME_M6  =6
MT5_TIMEFAME_M10 =10
MT5_TIMEFAME_M12 =12
MT5_TIMEFAME_M15 =15
MT5_TIMEFAME_M20 =20
MT5_TIMEFAME_M30 =30
MT5_TIMEFAME_H1  =1  | 0x4000
MT5_TIMEFAME_H2  =2  | 0x4000
MT5_TIMEFAME_H3  =3  | 0x4000
MT5_TIMEFAME_H4  =4  | 0x4000
MT5_TIMEFAME_H6  =6  | 0x4000
MT5_TIMEFAME_H8  =8  | 0x4000
MT5_TIMEFAME_H12 =12 | 0x4000
MT5_TIMEFAME_D1  =24 | 0x4000
MT5_TIMEFAME_W1  =1 | 0x8000
MT5_TIMEFAME_MON1=1 | 0xC000

#                              year , month, day, hour, minute,  tz
UTC_FROM = datetime.datetime(2018, 8,  1,0,0, tzinfo=pytz.timezone("Etc/UTC"))
UTC_TO   = datetime.datetime(2020, 3, 27,0,0, tzinfo=pytz.timezone("Etc/UTC"))

TIME_FRAME_DEFAULT= MT5_TIMEFAME_D1

#============
# 10.ABR.2020
#============
# removido PCAR3, dados incompletos no TRYD
# 

#============
# 15.04.2020
#============
# ativos DTEX3 e MRVE3 sempre com problemas 
# de leitura do preço de fechamento diário, retirar da lista
# de ativos, removidos

# DEFINE ACHAR VALOR MINIMO OU MAXIMO DE UMA SERIE
MAXIMO=1
MINIMO=0

STR_W1       = " W1"
STR_H1        = " H1"    
STR_D1    =     " D1"
STR_M30       = "M30"

TIME_FRAME_DEFAULT= MT5_TIMEFAME_D1

# porcentual fechamento em relação a media movel
DISTANCIA_MEDIA_MOVEL_M30 = 0.25  # em percentual
DISTANCIA_MEDIA_MOVEL_H1= 0.35      # em percentual
DISTANCIA_MEDIA_MOVEL_W1= 2.5      # em percentual

# ignoro ultimo candle (aberto) ou não
DROP_LAST_CANDLE = False

#######################################################################
# CONFIGURACAOES SETUP MM200
#######################################################################
S_200_MEDIA_MOVEL = 200  # media movel a detectar a proximidade
#######################################################################

#######################################################################
# CONFIGURACAOES SETUP IFR3
#######################################################################
MEDIA_SMA_IFR3 = 50   # ativo deve estar em tendencia
LAG_MEDIA_MOVEL_IFR3 = 17   # vejo os ultimos 15 periodos pra verificar tendencia
IFR3_TOLERANCIA_SMA = -0.0001    # threshold quando mm esta flat
IFR3_THRESHOLD_UP = 90       # IFR2 sobrecomprado threshold
IFR3_THRESHOLD_DOWN = 10     # IFR2 sobrevendio threshold
AVALIAR_TENDENCIA="Nao"
#######################################################################


######################################################################
# CONFIGURACAOES LS POR COINTEGRACAO
#######################################################################
# 10/04/2020 - removido PCAR3, dados incompletos no TRYD
# 15/04/2020 - ativos DTEX3 e MRVE3 sempre com problemas 
# 09/06/20   - removido OIBR3 (preço) e PDGR3,SEER3 (volume)
# 20/06/2020 - removido SULA11, nao atualiza desde 2010
# 29/06/2020 - removido CIEL3, KLBN4, POMO4, VIVR3  - preço menor que 5
# 10/08/2020 - reincluidos DTEX3 e MRVE3
# 01/09/2020 - removido BBDC3, CMIG3, ITUB3, LAME3,PETR3
# 07/09/2020 - removido TOTS3 (split ~100 dias)
# 

# # CARTEIRA
# LISTA_B3 = {'CIEL3', 'ITSA4','GGBR4','ENBR3','VVAR3','CSNA3','PETR4','TAEE11',
#             'BPAN4','COGN3','CEAB3','MRFG3','JHSF3','LOGN3','KLBN4','USIM5','OIBR3'}



# LISTA_B3 = {'ABEV3','ALPA4','ALUP11','ARZZ3','AZUL4','B3SA3','BBAS3',
#             'BBDC4','BBSE3','BEEF3','BIDI4','BOVA11','BRAP4','BRDT3','BRFS3','BRKM5',
#             'BRML3','BRSR6','BTOW3','CCRO3','CESP6','CMIG4',
#             'CPFE3','CPLE6','CRFB3','CSAN3','CSMG3','CSNA3','CVCB3','CYRE3','DTEX3',
#             'ECOR3','EGIE3','ELET3','ELET6','EMBR3','ENBR3','ENGI11','EQTL3',
#             'EZTC3','FLRY3','GFSA3','GGBR4','GOAU4','GOLL4','GRND3','GUAR3',
#             'HGTX3','HYPE3','IGTA3','IRBR3','ITSA4','ITUB4','JBSS3',
#             'KLBN11','COGN3','LAME4','LIGT3','LINX3','LREN3','MDIA3','MGLU3',
#             'MRFG3','MRVE3','MULT3','MYPK3','ODPV3','PETR4','PSSA3','QUAL3','RADL3','RAIL3',
#             'RAPT4','RENT3','RLOG3','SANB11','SAPR11','SBSP3','SLCE3','SMTO3','SMLS3',
#             'SUZB3','TAEE11','TIET11','TIMS3','TRPL4','TUPY3','UGPA3',
#             'USIM5','VALE3','VIVT4','VVAR3','WEGE3','JHSF3','LOGN3','CEAB3','OIBR3','BPAN4'}

LISTA_B3 = {'BBDC4','ITUB4','VALE3','VIVT4'}

# LISTA_B3 = {'FLRY3','MULT3','MRVE3','CCRO3','QUAL3','LREN3','ABEV3'}
 
STEP_OF_TEST = 10             # steps forward unitroot tests
TAM_AMOSTRA_UNIROOT= 100     # tamanho minimo da amostra para teste uniroot geralmente com n=100

  
AMOSTRA_LONGA = 260          # tamanho MINIMO da amostra para fazer todas os testes, pois o tamanho da amostra do teste uniroot
                             # é para 1 teste, caso queremos correr sobre a série, ela deve ter um tamanho maior.
                             # ATENCAO - SE MUDAR PARA OUTRO VALOR MAIOR QUE 260, VAI EXTRAPOLAR O GRAFICO "*" NR TESTES
                             # MAXIMO É 32.

VALOR_MIN_CORRELA = 0.40     # correlacao minima desejada de coef. correralacao de Pearson, 
                             # ira apresentar os pares com correlacao maior ou igua a VALOR_MIN_CORRELA
MIN_TEST_PASS_RATE= 0.50     # tem que passar em TEST_PASS_RATE dos testes janela movel
                             # diminuiu a volatilidade,,,aumentando pass rate
                         
IS_ADF= False                # adf ou phillips-perron?
OMLY_PASS = False            # só loga os testes que passaram

SPREAD_MINIMO = 1.5

LIMIAR_HORZ = 7.1
HORIZ_FIRST_VALUE = 1
HORIZ_LAST_VALUE  = 0
HORIZ_MEAN_VALUE  = 2 
HORIZ_DISP_RELAT  = 3  
HORIZ_CRITERIO    = HORIZ_DISP_RELAT  

Z_ALFA_0DOT05 = 0.05
Z_ALFA_0DOT01 = 0.01
Z_ALFA_0DOT10 = 0.10

P_VALOR_CRITICO_PP   = Z_ALFA_0DOT05     # se p-valor aumenta, mais dificil rejeitar Ho (não-coestacionariedade)
P_VALOR_CRITICO_KPSS = Z_ALFA_0DOT10   # se p-valor aumenta, rejeita com mais facilidade Ho (estacionariedade)
P_VALOR_CRITICO_REG  = Z_ALFA_0DOT05

 # valor usado para bandas de bollinger, volatilidade etc...geralmente
# é igual ao tamanho do tamanho mínimo dos testes uniroot
N_OTIMO = 160
DISTANCIA_RATIO_BB = 0.01  # razao

# True  = correlacao desabilitada
# False = correlacao minima requerida
COR_OFF = False

