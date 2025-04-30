# =============================================================================
# Autor: Giovanni Leopoldo Rozza - Abril - 2020
# Processa cointegração entre os ativos da B3
# 
# history
# versão | Data      | Atualizacao
#------------------------------------------------------------------------------
#  1.0   | 29.04.20  | Versão inicial
#  1.1   | 09.05.20  | Adicionado coluna planilha "Nr semanas cointegrado"
#        |           | usando coluna Z, que estava vazia
#  1.2   | 04.06.20  | Agora o script calcula a "horizontalidade" das bandas de 
#        |           | bollinger. 
#  1.3   | 16.06.20  | Filtro 10 ultimos testes pass rate de 80%
#  2.0   | 20.06.20  | Novo algo para realizacao dos testes de hipotese
#        |           | agora vou aumentando o tamanho da amostra adicionando
#        |           | o passado em steps fixos
#  2.1   | 23.06.20  | Removo os pares que não atendem a horizontalidade pre 
#        |           | pré-configurada
#  2.2   | 07.07.20  | Horizontalidade não é mais criterio, uso agora periodos
#        |           | [100,160,200] e também agora posto o grau de confianca
#        |           | [95,99%], teste de Chow para o tamanho da amostra, e
#        |           | também mudei o calculo para o calculo do half-life. 
#        |           | Faco regressão nMIN=30 e pulo de 2 em 2 para calcular a 
#        |           | dispersão relativa, fica mais sensivel.
#  2.3   |           | Monitoro o spread agora.
#  2.4   |  28.10.20 | Removido "horizontalidade" do print inicial 
# =============================================================================

import QuantUtilities as util
import QuantMT5ConstantesGlobais as CTE
import datetime
import numpy as np
from scipy.stats import pearsonr
import pandas as pd
import math
from arch.unitroot import PhillipsPerron
from arch.unitroot import KPSS
import scipy.linalg as la
import csv
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
import scipy
from scipy.stats import shapiro
from statsmodels.tsa.stattools import adfuller
#from scipy.stats import kstest 
import sys

def computa_ls_cointegracao(dict_preco_full: dict, file_relat):
    
    if ((CTE.AMOSTRA_LONGA - CTE.TAM_AMOSTRA_UNIROOT) % CTE.STEP_OF_TEST != 0):
        print("### ATENÇÃO ### Divisão (CTE.AMOSTRA_LONGA - CTE.TAM_AMOSTRA_UNIROOT) sobre CTE.STEP_OF_TEST tem que ser um número inteiro... ",file=file_relat)
        return    
    
    ativos_pass_ok = []
    residuos_pass_csv =[]
    
    # para console mostrar resultados (apesar de logar agora em arquivo)
    pd.options.mode.chained_assignment = None
    pd.set_option('display.max_rows', 500)
   
    # calcula o nr de testes a serem realizado  
          
    nr_testes = math.floor((CTE.AMOSTRA_LONGA - CTE.TAM_AMOSTRA_UNIROOT) / CTE.STEP_OF_TEST)
    
    dict_cpy = dict_preco_full.copy()
    
    # janela de tempo tem que ser maior ou igual a AMOSTRA_LONGA
    # porque mais 1, porque calculo a correlacao retornos, 1a linha vai embora
    
    print("\n")
        
    for kx_ativo, vx_preco in sorted(dict_preco_full.items()):

        #print("Testando cointegração ativo : " + idx_par[0] + " e " + idx_par[1] +  " ...")

        #########################################################################
        # le o denominador selecionado para horizontalidade
        #########################################################################              
        #vx_preco = dict_preco_full[idx_par[0]]
        #kx_ativo = idx_par[0]
   
        vx_preco = vx_preco.head(CTE.AMOSTRA_LONGA + 1)
              
        #############################################
        # 1a linha daframe é a mais recente!!
        # última linha mais antiga!!
        # log return = log(Price( [t]/Price[t-1] )
        #############################################
        
        vx_preco['log_ret']  = np.log(vx_preco['Fechamento']/ vx_preco['Fechamento'].shift(-1))


        ###################################################################################
        # elimino a ULTIMA linha pois é NaN (retorno do preco mais antigo não existe)
        ###################################################################################        
        vx_preco = vx_preco.iloc[:-1]
        
        lst_log_ret_X     = vx_preco['log_ret'].tolist()     
        lst_preco_close_X = vx_preco['Fechamento'].tolist()
          
        ############################################
        # remove ativo do loop primario do loop secundario
        ############################################
        dict_cpy.pop(kx_ativo, None)

        #########################################################################
        # le o denominador selecionado para horizontalidade
        #########################################################################
        #vy_preco = dict_preco_full[ idx_par[1]]
        #ky_ativo = idx_par[1]
        

        for ky_ativo, vy_preco in sorted(dict_cpy.items()):

            print("Testando cointegração ativo : " + kx_ativo + " e " + ky_ativo +  " ...")

            seq_testes_AB_ok= np.zeros(nr_testes+1,dtype=int)  # array de resultado dos testes (A--B)
            seq_testes_BA_ok= np.zeros(nr_testes+1,dtype=int)  # array de resultado dos testes (B--A)
            nr_sem_coint = 0
    
    
            ############################################################
            # dropo ultima linha lá embaixo, por isso conta mais 1 
            # armazena os CTE.AMOSTRA_LONGA + 1 dias mais recentes
            ############################################################
            
            vy_preco = vy_preco.head(CTE.AMOSTRA_LONGA + 1)                   
        
            #############################################
            # 1a linha daframe é a mais recente!!
            # última linha mais antiga!!
            # log return = log(Price( [t]/Price[t-1] )
            #############################################
            vy_preco['log_ret']  = np.log(vy_preco['Fechamento']/ vy_preco['Fechamento'].shift(-1))
         
    
            ###################################################################################
            # elimino a ULTIMA linha pois é NaN (retorno do preco mais antigo não existe)
            ###################################################################################           
            vy_preco = vy_preco.iloc[:-1]
                                   
            lst_log_ret_Y     = vy_preco['log_ret'].tolist()         
            lst_preco_close_Y = vy_preco['Fechamento'].tolist()
              
            ldatasDiferentes = False
    
            ########################################################################################
            # assegura que os preços estão sincronizados nas datas (row a row)
            ########################################################################################

            for ind in vy_preco.index: 
                         
                if not vy_preco['Data'][ind] == vx_preco['Data'][ind]: 
                    # NO ARQUIVO
                    print("### WARNING ### Data dos ativo "+kx_ativo + ' e ativo ' + ky_ativo + ' são diferentes ', file=file_relat  )
                    print('Data ativo ' + kx_ativo + ' : ' + vx_preco['Data'][ind] , file=file_relat) 
                    print('Data ativo ' + ky_ativo + ' : ' + vy_preco['Data'][ind] , file=file_relat) 
                    
                    # NA TELA
                    print("### WARNING ### Data dos ativo "+kx_ativo + ' e ativo ' + ky_ativo + ' são diferentes ' )
                    print('Data ativo ' + kx_ativo + ' : ' + vx_preco['Data'][ind] ) 
                    print('Data ativo ' + ky_ativo + ' : ' + vy_preco['Data'][ind] )                               
                    ldatasDiferentes= True
        
            if not ldatasDiferentes:                             
            
                ##############################################################
                # inicializa registros dos coeficientes das retas de regressão
                ##############################################################
                # lst_beta_AB = []
                # lst_beta_BA = []
                # p_stat_PP_AB_OLS = []
                # p_stat_PP_BA_OLS = []
                
                resultado_teste_AB = {}
                resultado_teste_BA = {}
                resultado_teste = {}
                
                for n_count in range(0, nr_testes+1):  
                        
                                       
                    # calcula correlação de pearson usando a janela de tempo dos testes UNIROOT                                       
                    # verifica se correlacao e maior ou igual a um valor critico e p-valor é menor que um valor critico
                                         
                    nIndexInicio =  0         # inicio é sempre o mesmo 
                    nIndexFim    =  CTE.TAM_AMOSTRA_UNIROOT + n_count * CTE.STEP_OF_TEST # a cada teste tamanho da amostra aumenta.

                    corr_pearson, _ = pearsonr(lst_log_ret_X[nIndexInicio: nIndexFim],lst_log_ret_Y[nIndexInicio: nIndexFim])   

                    # https://ncss-wpengine.netdna-ssl.com/wp-content/themes/ncss/pdf/Procedures/PASS/Confidence_Intervals_for_Pearsons_Correlation.pdf
                    ########    calcula o intervalo de confianca para CTE.VALOR_MIN_CORRELA  ########################                  
                    media_pearson = 0.5*np.log((1 + CTE.VALOR_MIN_CORRELA)/(1 - CTE.VALOR_MIN_CORRELA))
                    dp_pearson    = math.sqrt(1/(nIndexFim - 3))
                    z_ic_lower    = media_pearson - util.get_Z_alfa(CTE.P_VALOR_CRITICO_REG)*dp_pearson
                    z_ic_higher   = media_pearson + util.get_Z_alfa(CTE.P_VALOR_CRITICO_REG)*dp_pearson
                    r_lower_min   = (np.exp(2*z_ic_lower)  - 1)/(np.exp(2*z_ic_lower ) + 1)
                    
                    ########    calcula o intervalo de confianca para corr_pearson  ########################                  
                    
                    media_pearson = 0.5*np.log((1 + corr_pearson)/(1 - corr_pearson))
                    dp_pearson    = math.sqrt(1/(nIndexFim - 3))
                    z_ic_lower    = media_pearson - util.get_Z_alfa(CTE.P_VALOR_CRITICO_REG)*dp_pearson
                    z_ic_higher   = media_pearson + util.get_Z_alfa(CTE.P_VALOR_CRITICO_REG)*dp_pearson
                    r_lower       = (np.exp(2*z_ic_lower)  - 1)/(np.exp(2*z_ic_lower ) + 1)
                    r_higher      = (np.exp(2*z_ic_higher) - 1)/(np.exp(2*z_ic_higher) + 1)  
                    ############################################################################################ 
                   
                    #################################################################################################################
                    #                               |  0       |   1    |  2        |   3    |    4       |  5    |    6  |
                    # resultado_teste[nPeriodo] = [ p_valor_pp, pp_stat,p_valor_kpss,beta_reg,last_residuo,r_lower,r_higher ]
                    #
                    ##################################################################################################################

                    #so testa KPSS e PP se correlacao ok no período, e portanto o limite inferior
                    # do IC não pode ser negativo
                    
                    if ( r_lower_min > 0 and corr_pearson > r_lower_min) or CTE.COR_OFF:
                                    
                        ################################################
                        # regressao Y ~ X1 (A-->B) OLS
                        ################################################
                        p_valor_pp_AB,pp_stat_AB,p_valor_kpss_AB,beta_reg_AB,array_spread_AB = computa_pp_kpss_OLS(np.array(lst_preco_close_X[ nIndexInicio: nIndexFim]),
                                                                                             np.array(lst_preco_close_Y[ nIndexInicio: nIndexFim  ]))
                                                               
                        # armazeno o beta da reta de regressão
                        # lst_beta_AB.append(beta_reg)
 
                        # pp_pvalue < P_VALOR_CRITICO e kpss_p_value > P_VALOR_CRITICO (A-->B e B-->A)
                        # pois pp Hip. alternativa é estacionaria e no kpss Hip. nula é estacionaria                            
                               
                        # testes AB [ 0 , 0, 0 .....] se passa substitui [index]=1
                        if p_valor_pp_AB < CTE.P_VALOR_CRITICO_PP and p_valor_kpss_AB > CTE.P_VALOR_CRITICO_KPSS:
                            seq_testes_AB_ok[n_count] = 1           # teste AB passou
                            
                        ################################################
                        # regressao X1 ~ Y (B-->A) OLS
                        ###############################################                                
                        p_valor_pp_BA,pp_stat_BA,p_valor_kpss_BA,beta_reg_BA,array_spread_BA = computa_pp_kpss_OLS(np.array(lst_preco_close_Y[ nIndexInicio: nIndexFim]),
                                                                                             np.array(lst_preco_close_X[ nIndexInicio: nIndexFim  ]))
                                                               
                        # armazeno o beta da reta de regressão
                        # lst_beta_BA.append(beta_reg)                    
        
                        # testes AB [ 0 , 0, 0 .....] se passa substitui [index]=1
                        if p_valor_pp_BA < CTE.P_VALOR_CRITICO_PP and p_valor_kpss_BA > CTE.P_VALOR_CRITICO_KPSS:
                            seq_testes_BA_ok[n_count] = 1           # teste AB passou                               
                            
                        ################################################
                        # regressao via OTS / PCA 
                        ################################################
                        p_valor_pp_OTS = computa_pp_OTS(np.array(lst_preco_close_X[nIndexInicio: nIndexFim]),
                                                        np.array(lst_preco_close_Y[nIndexInicio: nIndexFim  ]))
                        
                        # se não passa, falha o teste e segue o baile
                        if  p_valor_pp_OTS > CTE.P_VALOR_CRITICO_PP:
                            seq_testes_AB_ok[n_count] = 0
                            seq_testes_BA_ok[n_count] = 0
                        
                        # se passa registra o p_valor                      
                        else:
                            if seq_testes_AB_ok[n_count] == 1:
                                # p_stat_PP_AB_OLS.append( [pp_stat_AB,nIndexFim,p_valor_pp_AB] ) # anota valor do p_valor teste AB
                                resultado_teste_AB[ nIndexFim ] = [p_valor_pp_AB,
                                                                   pp_stat_AB,
                                                                   p_valor_kpss_AB,
                                                                   beta_reg_AB,
                                                                   array_spread_AB,
                                                                   r_lower,
                                                                   r_higher]
                                
                            if seq_testes_BA_ok[n_count] == 1:
                                # p_stat_PP_BA_OLS.append( [pp_stat_BA,nIndexFim,p_valor_pp_BA] ) # anota valor do p_valor teste AB 
                                resultado_teste_BA[ nIndexFim ] = [p_valor_pp_BA,
                                                                   pp_stat_BA,
                                                                   p_valor_kpss_BA,
                                                                   beta_reg_BA,
                                                                   array_spread_BA,
                                                                   r_lower,
                                                                   r_higher]                                

                lPassou = False
                ativo_ind = kx_ativo
                ativo_dep = ky_ativo
                pass_rate = 0.0
                str_pass = "FAIL"
                str_AB_BA = "AB"
                
                if np.sum(seq_testes_AB_ok) < np.sum(seq_testes_BA_ok):
                    ################################################
                    # se BA tem maior nr de testes...troca ativos   
                    ################################################
                    ativo_ind = ky_ativo
                    ativo_dep = kx_ativo
                    str_AB_BA = "BA"

                    resultado_teste = resultado_teste_BA
                    
                    # superou pass rate?
                    pass_rate = np.sum(seq_testes_BA_ok)/(nr_testes + 1)
                    
                    seq_testes_ok = seq_testes_BA_ok      
                                             
                    # se AB kx_ativo (IND) e ky_ativo (DEP) 
                else:
                    resultado_teste = resultado_teste_AB
                    
                    # superou pass rate?
                    pass_rate = np.sum(seq_testes_AB_ok)/(nr_testes + 1)
                    
                    seq_testes_ok = seq_testes_AB_ok  
                     
                if pass_rate  >= CTE.MIN_TEST_PASS_RATE: 
                    li = seq_testes_ok.tolist()
                    li.reverse()
                    # se tem ao menos um FAILED test
                    if not np.sum(li) == (nr_testes + 1):
                        nr_sem_coint = len(li) - 1 - li[::-1].index(0)
                        nr_sem_coint = len(li) -  nr_sem_coint -1  
                    else:
                        nr_sem_coint = (nr_testes + 1)                                               
                    #seq_testes = seq_testes_AB_ok
                    lPassou = True
                    str_pass = "PASS"
                
                str_pass_rate = str(round(pass_rate*100,2))  
                
                # se ONLY_PASS = TRUE só imprime se passou o teste
                if  (lPassou or not CTE.OMLY_PASS):
                    print("COINT TEST  ["+str_AB_BA +"]  |" + ativo_ind.rjust(7, ' ') + " e " + ativo_dep.rjust(7, ' ')  +
                          "  | PASS RATE: " + str_pass_rate.rjust(6,' ') + " %  || RESULTADO: < " 
                          + str_pass +" >", file=file_relat)  
                    
                    # print("COINT TEST  ["+str_AB_BA +"]  |" + ativo_ind.rjust(7, ' ') + " e " + ativo_dep.rjust(7, ' ')  +
                    #       "  | PASS RATE: " + str_pass_rate.rjust(6,' ') + " %  || RESULTADO: < " 
                    #       + str_pass +" >")                          
                
                #if True:   # DEBUG
                    
                if  lPassou:  
                
                    ###########################################################################################
                    #  Aqui identifico qual os períodos que apresentam spread acima de +/-CTE.SPREAD_MINIMO,
                    #  caso apareca mais de um, conto os periodos e publico quem está mais cointegrado no
                    #  momento
                    ###########################################################################################
                    
                    # resultado_teste[k_periodo][0] = p_valor_pp
                    # resultado_teste[k_periodo][1] = pp_stat
                    # resultado_teste[k_periodo][2] = p_valor_kpss
                    # resultado_teste[k_periodo][3] = beta_reg
                    # resultado_teste[k_periodo][4] = array_spread
                    # resultado_teste[k_periodo][5] = r_lower
                    # resultado_teste[k_periodo][6] = r_higher
                    
                    nr_periods_spread_min = 0
                    melhor_periodo = -1
                    melhor_alfa ="95"
                    min_stat_valor = 0   
                    beta_otimo = -1                                       
                    melhor_vol_beta = 9999
                    
                    ####################################################################################
                    # para escolher o par identifico quem está atingindo os limites +/-CTE.SPREAD_MIN
                    # e dentro deste selecionos o com menor dispersão relativa do beta já que todos passaram 
                    # no teste de coestacionariedade
                    #####################################################################################
                    beta_global = [] #dispersão relatva do beta em relacao a todos os períodos cointegrados com teste=PASS.  
                    
                    for k_periodo in resultado_teste.keys():
                        
                        ############ AVALIA DISPERSÃO DA REGRESSAO LINEAR ##############################
                        # JANELA MOVEL DE 30 PERIODOS DE 2 EM 2 VALOR
                        ################################################################################                                               
                        beta_global.append(resultado_teste[k_periodo][3])
                        
                        # tamanho da regressao são 30 valores qq n
                        # adiciona 2 novas observacoes a cada nova regressao
                        # de forma a adicionar 35 novas regressões para amostra minima de 100 observações
                        
                        salto=2
                        inicio_beta = 30
                        passo = int( (k_periodo - inicio_beta)/salto)
                        betas = []     
                        
                        # calculo as regressoes 40 periodos jan movel de 2 periodos
                        for idx in range(0, passo + 1 ):   
                            X_ind, Y_dep = retorna_df_AB_ou_BA(str_AB_BA,
                                                               lst_preco_close_X[ idx*salto: inicio_beta + idx*salto] ,
                                                               lst_preco_close_Y[ idx*salto: inicio_beta + idx*salto] )
                            
                            reg_linear = LinearRegression(fit_intercept = True)
                            #Train:
                            reg_linear.fit(X_ind, Y_dep) 
                            # 1o coeficiente [ [] ]
                            betas.append(reg_linear.coef_[0,0])                            
                        
                        # agora calculo a volatilidade do beta 
                        # https://www.macroption.com/historical-volatility-calculation/
                        df_beta = pd.DataFrame( { 'beta' : betas  } )               
                        
                        df_beta['vol_beta']  = np.log(df_beta['beta']/ df_beta['beta'].shift(-1)) 
                        
                        df_beta = df_beta.iloc[:-1] # ultima linha é NaN
                                                
                        vol_beta = (np.std(df_beta['vol_beta'] .tolist()))*100
                           
                        # print(df_beta) # DEBUG
                        # print(vol_beta) # DEBUG
                        
                        arr_spread = resultado_teste[k_periodo][4]
                        
                        last_spread_z =  ( arr_spread[0] - np.mean(arr_spread))/np.std(arr_spread)
                        
                        # DEBUG
                        # print('k_periodo')
                        # print(k_periodo)
                        # print('resultado_teste[k_periodo][3]')
                        # print(resultado_teste[k_periodo][3])
                        # print('arr_spread[0]')
                        # print(arr_spread[0])
                        # 
                        # print("last_spread_z")
                        # print(last_spread_z)
                        # print('np.mean(arr_spread)')
                        # print(np.mean(arr_spread))
                        # print('np.std(arr_spread)')      
                        # print(np.std(arr_spread))
                        # print('------------')
                        # DEBUG       
                        
                        # aqui verifico se o beta troca de sinal, se troca de sinal (null) ignoro...pois está perto do zero.
                        if  ( last_spread_z > CTE.SPREAD_MINIMO or last_spread_z< -1* CTE.SPREAD_MINIMO) and not df_beta.isnull().values.any() :
                            
                            nr_periods_spread_min = nr_periods_spread_min +1
                            
                            # se beta for melhor que o anterior
                            if vol_beta < melhor_vol_beta:
                               results_sw             = shapiro(np.array(df_beta['vol_beta'] )) # saphiro-wilk
                               #results_sw              = kstest(np.array(df_beta['vol_beta'] ),"norm") # kolgomorov
                               #print(results_sw)     # debug
                               melhor_periodo         = k_periodo
                               beta_otimo             = resultado_teste[k_periodo][3]
                               melhor_spread          = arr_spread
                               IC_r_low               = resultado_teste[k_periodo][5]
                               IC_r_high              = resultado_teste[k_periodo][6]
                               melhor_vol_beta        = vol_beta
                            
                               # define qual o alfa
                               if resultado_teste[k_periodo][0]  <= 0.01:
                                   melhor_alfa = "99"                           

                        # agora calculo a dispersão do beta em relacao a todos os períodos cointegrados.                                 
                        coef_disp_beta_global =  ( np.std(beta_global)/np.mean(beta_global) )*100 

                    if not melhor_periodo == -1:
                        
                        ################################################################################ 
                        #                      ### TESTE DE CHOW  ###
                        # primeiro nível - 0..............melhor_nivel/2...............melhor_mivel
                        # verifica atraves do teste de Chow descontinuidade da reta de regressão
                        ################################################################################
                        # k = numero de parametros no caso são 2
                        # N1 = numero de amostras a
                        # N2 = numero de amostras b
                        # RSS_ab = SSR amostra total (a+b)
                        # RSS_a  = SSR amostra a
                        # RSS_b  = SSR amostra b
                        # chow = ((RSS_ab-(RSS_a + RSS_b))/k)/((RSS_a+RSS_b)/(N1+N2-2*k))
                        ################################################################################                             
                        
                        X_ind,Y_dep = retorna_df_AB_ou_BA(str_AB_BA,
                                                           lst_preco_close_X[ 0:melhor_periodo ],
                                                           lst_preco_close_Y[ 0:melhor_periodo ] )
                        
                        X_a,Y_a     =  retorna_df_AB_ou_BA(str_AB_BA,
                                                           lst_preco_close_X[ 0 : int(melhor_periodo/2) ] ,
                                                           lst_preco_close_Y[ 0 : int(melhor_periodo/2) ] )
                        
                        X_b,Y_b    =   retorna_df_AB_ou_BA(str_AB_BA,
                                                           lst_preco_close_X[ int(melhor_periodo/2) : melhor_periodo ] ,
                                                           lst_preco_close_Y[ int(melhor_periodo/2) : melhor_periodo ] )                        
                        X_ind    = sm.add_constant(X_ind)                              
                        model_ab = sm.OLS(Y_dep,X_ind).fit()    # 1a variavel é a dependente!
                        RSS_ab   = model_ab.ssr
                        
                        X_a    = sm.add_constant(X_a) 
                        model_a = sm.OLS(Y_a,X_a).fit()         # 1a variavel é a dependente!
                        RSS_a   = model_a.ssr
            
                        X_b    = sm.add_constant(X_b) 
                        model_b = sm.OLS(Y_b,X_b).fit()         # 1a variavel é a dependente!
                        RSS_b   = model_b.ssr
                        
                        # GRAU DE CONFIANCA 99%
                        chow_n1 = ((RSS_ab- (RSS_a + RSS_b) )/2)/( (RSS_a + RSS_b)/(len(X_a) + len(X_b) - 4) )            
                        
                        #p_valor_chow = scipy.stats.f.cdf(chow, 2, len(X_a) + len(X_b) - 4)
                        F_critico_chow_n1 = scipy.stats.f.ppf( 1-CTE.Z_ALFA_0DOT01, 2, len(X_a) + len(X_b) )
                        
                        str_L1_passou ="NÃO"
                        if chow_n1 < F_critico_chow_n1:
                            str_L1_passou="SIM"
    
                        print("PAR : " + ativo_ind +'/' + ativo_dep,file=file_relat)
                        print("### NIVEL 1 ### Estatistica F Crítico GL=2, n=" + str(melhor_periodo) + " alfa=0,01 : " + 
                              str(round(F_critico_chow_n1,3)) + " Estatística Chow Test : " + str(round(chow_n1,3)) + 
                              " [" + str_L1_passou +"]" ,file=file_relat )
                        print("------------------------------------------------------------------------------------------------------------------",file=file_relat)
                        print("\n",file=file_relat )     
            
                                                                                                
                        #############################################################################
                        # calculo o half-life baseado na regressão OLS do spread com lag 1 período e de 
                        # diff(spread - lag 1 período  )
                        ##############################################################################
                        
                        # df.iloc[0][0] -> seleciona linha 0 da coluna 0
                        # df.iloc[1][0] -> seleciona linha 1 da coluna 0
                        # df.iloc[1]['colunm_name'] -> seleciona linha 1 da coluna "colunm_name"
                        
                        # Run OLS regression on spread series and lagged version of itself
                        # https://www.pythonforfinance.net/2016/05/09/python-backtesting-mean-reversion-part-2/ 
                        
                        
                        df1 = pd.DataFrame({'spread':melhor_spread })                    
                          
                        spread_lag =pd.DataFrame({'spread':df1.spread.shift(1) })
    
                        spread_lag.iloc[0]['spread':] = spread_lag.iloc[1]['spread':]
                        
                        spread_ret = pd.DataFrame({'spread':np.array(df1['spread']) - np.array(spread_lag['spread']) })
                                                                    
                        spread_ret.iloc[0]['spread':]= spread_ret.iloc[1]['spread':]
                        
                        # An intercept is not included by default and should be added by the user. 
                        # See statsmodels.tools.add_constant.    
                        spread_lag2 = sm.add_constant(spread_lag)             
                        model = sm.OLS(spread_ret,spread_lag2)
                        res = model.fit()
                        half_life =   -np.log(2) / res.params[1] 
                         
                        ################################################################                      
                        # DEPRECATED 07.07.20, APESAR DOS RESULTADOS SEREM PARECIDOS
                        # AQUI USO REGRESSAO OTS, E AUTOVALORES PARA ACHAR O 
                        # SPREAD E AUTOCORRELAÇÃO ENTRE O SPREAD E A VERSÃO
                        # LAGUEADA
                        ################################################################
                        # s1 = np.array(lst_preco_close_X[0:melhor_periodo] ) 
                        # s2 = np.array(lst_preco_close_Y[0:melhor_periodo] ) 
                        
                        # # calcula autovetores, autovetores e covariancia
                        # eigvals, eigvecs = la.eig(np.cov(s1,s2))
            
                        # if eigvals.real[0] < eigvals.real[1]:
                        
                        #     hedge  =  eigvecs[1,1]/eigvecs[0,1]                                                
                        # # se maior autovalor for a 1a coluna da matriz
                        # else:
                        #     hedge  =  eigvecs[1,0]/eigvecs[0,0]                             
                        
                        # spread = s2 - s1*hedge 
                        
                            #         # OLS
                            #         # df_dados = pd.DataFrame({"X1": lst_preco_close_X,  "Y": lst_preco_close_Y})
                            #         # results = sm.ols(formula='Y ~ X1', data=df_dados).fit()
                            #         # Y_pred = results.predict(df_dados[["X1"]])
                            #         # spread = df_dados["Y"].values - Y_pred 
                                    
                            #         #spread_serie  = pd.Series(spread, name='Spread')
                            #         #spread_lag    = spread_serie.shift(1)
                            #         # print(spread_serie['Spread'])
                            #         # print(spread_lag['Spread'])
                            
                        # phi1 do AR(1) é autocorrelacao de Xk e Xk-1
                        
                        # spread_lag = np.roll(spread,1)
                        # spread_lag[0]=spread_lag[1]
                        # phi1 = np.corrcoef(spread,spread_lag)    # novo
                                                            
                        # str_half_life =   str( round(-np.log(2) / np.log(np.abs(phi1[0,1])),2)  )
                                            
                        ##############################################################################################
                        # calculo desvio padrão e media do spread para avaliar em tempo real   
                        # alem de criar a linha com os valores do residuo na 2a planilha
                        ##############################################################################################                    
                        
                        # vetor de residuos
                        spread_z = (melhor_spread - np.mean(melhor_spread) )/np.std(melhor_spread)
                        
                        # inverte ordem para o mais recente aparecer
                        # a direita no gráfico
                        
                        spread_z = spread_z[::-1]
                         
                        str_spread = ""
                        
                        # ='Long & Short'!W2
                        str_padd=""
                        
                        if not residuos_pass_csv:
                            idx = 3
                        else:
                            idx = 3 + len(residuos_pass_csv)
                        if not melhor_periodo == CTE.AMOSTRA_LONGA:
                            str_padd = "0|"*(CTE.AMOSTRA_LONGA - melhor_periodo)
                        
                        for res in spread_z:
                            str_spread = str_spread + str( round(res,4) ) + '|'
                        str_spread = str_spread +  "='Long & Short'!W" + str(idx) + '|'       
                        str_spread = str_spread.replace('.',',')
                        str_spread = str_padd + str_spread
                        residuos_pass_csv.append([ativo_ind, ativo_dep,str_spread])
                         
                        # prepara as strings...
                        str_mean_spread = str( round( np.mean(melhor_spread),4))
                        str_std_spread  = str( round( np.std(melhor_spread), 4))                         
                        str_beta_otimo  = str( round(beta_otimo ,4) )
                        str_half_life   = str( round(half_life ,2) )
                        str_coef_disp_beta_global = str(round( coef_disp_beta_global,2))
                        str_IC_r_low  = str(round(IC_r_low,2))
                        str_IC_r_high = str(round(IC_r_high,2))
                        str_melhor_vol_beta = str(round(melhor_vol_beta,2))
                         
                        str_mean_spread = str_mean_spread.replace('.',',')
                        str_std_spread  = str_std_spread.replace('.',',')
                        str_beta_otimo  = str_beta_otimo.replace('.',',')
                        str_half_life   = str_half_life.replace('.',',')
                        str_pass_rate   = str_pass_rate.replace('.',',')
                        str_coef_disp_beta_global = str_coef_disp_beta_global.replace('.',',')
                        str_IC_r_low = str_IC_r_low.replace('.',',')
                        str_IC_r_high= str_IC_r_high.replace('.',',')
                        str_melhor_vol_beta = str_melhor_vol_beta.replace('.',',')
                        str_beta_normal ="NÃO"
                        if results_sw[1] > CTE.Z_ALFA_0DOT05:
                            str_beta_normal = "SIM"
                                               
                                      
                        ativos_pass_ok.append([ ativo_ind, ativo_dep, str_pass_rate, str_half_life, melhor_alfa ,str_L1_passou,
                                                str(nr_periods_spread_min),str_coef_disp_beta_global,str_melhor_vol_beta,
                                                str_mean_spread, str_std_spread, str_beta_otimo,
                                                str_IC_r_low,str_IC_r_high,
                                                "0","0",
                                                "0","0",
                                                "0","0", 
                                                str_beta_normal,
                                                str(nr_sem_coint),min_stat_valor, 
                                                str(melhor_periodo)] )
                
            else:
                print("## ATENÇÂO  ### Datas não estão sincronizadas, verifique o arquivo de logs")
                    
    print("\n") 
    print("\n")            
    print("|----------------------------------------------------------------------------------------------------------------|",file=file_relat)
    print("|                                               RELATÓRIO PARES COINTEGRADOS                                     |",file=file_relat)
    print("|----------------------------------------------------------------------------------------------------------------|",file=file_relat)
    print("|                                                                                                                |",file=file_relat)
    print('| DATA/HORA..................: ' + datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S %Z%z')+"                                                              |",file=file_relat)
    print("| TIMEFRAME..................:" + util.get_str_timeframe()+"                                                                                |",file=file_relat)
    print("| P-VALOR REG. LINEAR........: {0:5.3f}                                                                             |".format(CTE.P_VALOR_CRITICO_REG),file=file_relat)
    print("| P-VALOR PHILLIPS-PERRON....: {0:5.3f}                                                                             |".format(CTE.P_VALOR_CRITICO_PP),file=file_relat)
    print("| P-VALOR K.P.S.S............: {0:5.3f}                                                                             |".format(CTE.P_VALOR_CRITICO_KPSS),file=file_relat)
    print("| CORRELAÇÃO MÍNIMA..........: {0:4.2f}                                                                              |".format(CTE.VALOR_MIN_CORRELA),file=file_relat)             
    print("| JANELA TESTES UNIROOT......: {0:3d} períodos                                                                      | ".format(CTE.TAM_AMOSTRA_UNIROOT),file=file_relat) 
    print("| JANELA TOTAL...............: {0:3d} períodos                                                                      |".format(CTE.AMOSTRA_LONGA),file=file_relat)
    print("| STEPS TESTE UNIROOT........: {0:3d} períodos                                                                      |".format(CTE.STEP_OF_TEST) ,file=file_relat)
    print("| PASS RATE..................: {0:5.2f} %                                                                           |".format(CTE.MIN_TEST_PASS_RATE*100),file=file_relat)             
    print("|----------------------------------------------------------------------------------------------------------------|",file=file_relat)
    
    print("Preparando planilhas excel...")
    print("\n" )   
    
    ativos_cointegrados_csv = []  
    nr_linha = 3  # linha planilha excel
        
    if ativos_pass_ok:
        
        # removi porque preciso da mesma ordem nas duas planilhas       
        # sorted_list=sorted(ativos_pass_ok, reverse=True, key=lambda ativ : ativ [2])
                
        for par_ativo in ativos_pass_ok:
            
            numer = dict_preco_full[ par_ativo[0] ]  # variavel independente
            denom = dict_preco_full[ par_ativo[1] ]  # variavel dependente
            list_num = numer["Fechamento"].tolist()  
            list_den = denom["Fechamento"].tolist()  
            
            
            # ############ AVALIA DISPERSÃO DA REGRESSAO LINEAR ##############################
            # # JANELA MOVEL DE 40 PERIODOS DE 2 EM 2 VALORES
            # ################################################################################
            
            # passo = int((par_ativo[23] - 40)/2)
            # betas = []            
            

            # for idx in range(0, passo + 1 ):
            #     X_ab = pd.DataFrame({ 'X1': list_num[ idx*2: 40 + idx*2 ] }, columns = ["X1"])
            #     Y_ab = pd.DataFrame({ 'Y' : list_den[ idx*2: 40 + idx*2 ] }, columns = ["Y"])                
            #     reg_linear = LinearRegression(fit_intercept = True)
            #     #Train:
            #     reg_linear.fit(X_ab, Y_ab)  
            #     betas.append(reg_linear.coef_[0,0])
                    
            # # agora calculo a dispersão do beta            
            # coef_disp_beta = str( round((np.std(betas)/np.mean(betas))*100,2))
            # coef_disp_beta = coef_disp_beta.replace('.',',')                

            
       


            ratio = [x/y for x, y in zip(list_num, list_den)]
            df_ratio = pd.DataFrame(ratio, columns = ['Ratio']) 
          
            # reverto a serie no calculo [::-1]], senao ele desconsidera os nPeriodo rows mais atuais nPeriodo          
            df_ratio['SMA_OTM_mean'] = df_ratio['Ratio'][::-1].rolling(window = int( par_ativo[23] ) ).mean()
             
            last_ratio_mean = str( round( df_ratio['SMA_OTM_mean'][0],4))
            last_ratio_mean = last_ratio_mean.replace('.',',')
            
            # reverto a serie no calculo [::-1]], senao ele desconsidera os nPeriodo rows mais atuais
            df_ratio['SMA_OTM_std' ] = df_ratio['Ratio'][::-1].rolling(window = int( par_ativo[23] )).std()
            
            last_ratio_std = str( round( df_ratio['SMA_OTM_std'][0],4))
            last_ratio_std = last_ratio_std.replace('.',',')
                        
            last_ratio_z = str(round( ( df_ratio['Ratio'][0] - df_ratio['SMA_OTM_mean'][0])/df_ratio['SMA_OTM_std'][0],2))
            last_ratio_z = last_ratio_z.replace('.',',')
            
            
            if(df_ratio["Ratio"][0] > df_ratio["SMA_OTM_mean"][0]):
                
                str_buy = par_ativo[1]                          # OK
                
                str_nr_cotas_buy = '=MARRED($AL$1/S?;100)'      #OK    ativo[0] == j3 ativo[1] == s3
                str_valor_buy = "=AF?*S?"
                
                str_sell = par_ativo[0]
                
                str_nr_cotas_sell = '=MARRED($AL$1/J?;100)'
                str_valor_sell  = "=AI?*J?"

  
            else:
                str_buy = par_ativo[0]
                
                str_nr_cotas_buy = '=MARRED($AL$1/J?;100)'
                str_valor_buy = "=AF?*j?"
               
                str_sell = par_ativo[1]
                
                str_nr_cotas_sell = '=MARRED($AL$1/S?;100)'
                str_valor_sell  = "=AI?*S?"
                                   

            # ativo_ind         [0]
            # ativo_dep         [1]
            # pass_rate         [2]
            # half_life         [3]
            # melhor_alfa       [4]   
            # str_L1_passou     [5]  
            # nr_periods_spread_min [6]  
            # str_min_disp_relativa_beta [7] 
            # str_melhor_vol_beta [8]  
            # str_mean_spread       [9]
            # str_std_spread        [10]
            # beta_otimo        [11]
            # str_IC_r_low      [12]  
            # str_IC_r_high     [13]  
            # mean_vol_neg_ind  [14] # empty
            # std_vol_neg_ind   [15] # empty
            # mean_vol_pos_dep  [16] # empty
            # std_vol_pos_dep   [17] # empty
            # mean_vol_neg_dep  [18] # empty
            # std_vol_neg_dep   [19] # empty
            # str_beta_normal   [20]  
            # nr_sem_coint      [21]
            # pp_stat_valor     [22]
            # melhor_periodo    [23]

            
            form5 =  "=(U? - " + last_ratio_mean + ")/" + last_ratio_std  
            form5 = form5.replace('?',str(nr_linha))
            
            form6 = "=((S? - AC?*J?) - " + par_ativo[9] +")/" + par_ativo[10]
            form6 = form6.replace('?',str(nr_linha))
            
            form7 = "= 100*" + last_ratio_std + "/" + last_ratio_mean
            
            form8 = "= ABS( 100*" + par_ativo[10] + "/" + par_ativo[9]+")"
            
            # horizontalidade das BB

            numer = dict_preco_full[  par_ativo[0] ]
            denom = dict_preco_full[  par_ativo[1] ]
            
            soma_erro_L_U = str(calula_valor_ls_horizontalidade(numer, denom, CTE.HORIZ_CRITERIO, int( par_ativo[23]) ) )
                        
                                              #b3              #c3         #d3      #e3         #f3
            ativos_cointegrados_csv.append([par_ativo[0], "0", "0", "0", "0","0","0","0", "=Stech|COT!" + par_ativo[0] + ".Ult" ,
                                            par_ativo[1], "0", "0", "0", "0","0","0","0", "=Stech|COT!" + par_ativo[1] + ".Ult" ,
                                                                         last_ratio_z, "=Stech|COT!" + par_ativo[0] + ".Ult/Stech|COT!" + par_ativo[1] +".Ult", 
                                                                         form5, form6,par_ativo[7] , form7,par_ativo[21],form8,par_ativo[2] ,
                                                                         par_ativo[11],par_ativo[3],
                                                                         str_buy,str_nr_cotas_buy.replace('?',str(nr_linha)),str_valor_buy.replace('?',str(nr_linha)),
                                                                         str_sell,str_nr_cotas_sell.replace('?',str(nr_linha)),str_valor_sell.replace('?',str(nr_linha)),
                                                                         "0","0",
                                                                         "0",par_ativo[20],
                                                                         par_ativo[8],par_ativo[5], 
                                                                         par_ativo[6],"["+par_ativo[12] +" - " + par_ativo[13] +"]",
                                                                         par_ativo[4], 
                                                                         par_ativo[23], 
                                                                         soma_erro_L_U.replace('.',',')] )
            # novo par
            nr_linha = nr_linha + 1
                            
    pd.options.mode.chained_assignment = "warn"

    # salva lista de ativos cointegrados para monitoracao
    # with open('Ativos_cointegrados_lista_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.csv', 'w', newline='') as myfile:
    #  wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
 
    
    str_path_excel = "C:\\Users\\rgiovann\\OneDrive\\AULAS\Bagozzi\\PYTHON_SOURCE\\FINANCAS_QUANTITATIVAS\\PLANILHAS\\Ativos_cointegrados_lista_"
    with open(str_path_excel + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.csv', 'w', newline='\n') as csvfile:
        csvwriter = csv.writer(csvfile,delimiter =';')
        # 'Numerador','Denominador','Preço_NUM','Preço_DEN','Ratio_Ult' 'Ratio Inst' 'Ratio_medio','Ratio_2D_minus','Ratio_2D_plus','Ratio_3D_minus','Ratio_3D_plus','Ratio_4D_minus','Ratio_4D_plus' 
        csvwriter.writerows(ativos_cointegrados_csv)
        
    # salva residuos
    str_path_excel = "C:\\Users\\rgiovann\\OneDrive\\AULAS\Bagozzi\\PYTHON_SOURCE\\FINANCAS_QUANTITATIVAS\\PLANILHAS\\Ativos_cointegrados_residuos_"
 
    with open(str_path_excel + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.csv', 'w', newline='\n') as csvfile:
        csvwriter = csv.writer(csvfile,delimiter =';',quoting=csv.QUOTE_MINIMAL)
        # 'Numerador','Denominador','Preço_NUM','Preço_DEN','Ratio_Ult' 'Ratio Inst' 'Ratio_medio','Ratio_2D_minus','Ratio_2D_plus','Ratio_3D_minus','Ratio_3D_plus','Ratio_4D_minus','Ratio_4D_plus' 
        csvwriter.writerows(residuos_pass_csv)     

    return

###################################################################################################################################
###################################################################################################################################

def computa_pp_kpss_OLS(varInd,varDep):
        
    ################################################
    # regressao Y ~ X1 (A-->B) OLS
    ################################################
  
    X = np.array( varInd )
    Y = np.array( varDep )
                  
    Xres = X.reshape(-1,1)
    regressor = LinearRegression()
    regressor.fit(Xres, Y)
                                    
    # calculo o resíduo
    residuo = Y - (regressor.intercept_ + regressor.coef_[0]*X) 
    
    # calcula o spread
    spread  = Y - (regressor.coef_[0]*X)   
                        
    # residuo, supoe-se cte=0
    if not CTE.IS_ADF:
        ppTest = PhillipsPerron(residuo, trend='c')
        p_valor = ppTest.pvalue
        valor_critico = ppTest.stat
    else:
        adfTest = adfuller(residuo, autolag='AIC')
        p_valor = adfTest[1]            # estatistica
        valor_critico = adfTest[0]      # p_valor
        
    kpssTest    = KPSS(residuo)                                  
    kpss_pvalor = kpssTest.pvalue
    
    # kpss_pvalor = 0.5    # debug
    
    # retorno o valor dos testes de coestacionariedade e o array de residuo
    
    return p_valor,valor_critico,kpss_pvalor,regressor.coef_[0],spread

###################################################################################################################################
###################################################################################################################################

def computa_pp_OTS(varInd,varDep):

    ################################################
    # regressao via OTS / PCA 
    ################################################

    # calcula autovetores, autovetores e covariancia
    eigvals, eigvecs = la.eig(np.cov(varInd,varDep))
 
    # matriz de autovetores
    # [   a00  a01  ]
    # [   a10  a11  ]
    # se maior autovalor é o 1o elemento -> hedge = a10/a00
    # se maior autovalor é o 2o elemento -> hedge = a11/a01
     
    # 2a coluna de autovetor é a maior...
    if eigvals.real[0] < eigvals.real[1]:
     
        hedge  =  eigvecs[1,1]/eigvecs[0,1]                                                
    # se maior autovalor for a 1a coluna da matriz
    else:
        hedge  =  eigvecs[1,0]/eigvecs[0,0]                             
    
    spread = varDep - varInd*hedge    
     
    ####################################################
    # só faço Phillips-Perron para OTS
    # se não passa invalido tanto AB quanto BA
    ####################################################
    # aqui pode existir uma constante
    
    # residuo, supoe-se cte=0
    if not CTE.IS_ADF:
        ppTest = PhillipsPerron(spread, trend='c')
        p_valor = ppTest.pvalue   # p_valor
    else:
        adfTest = adfuller(spread, autolag='AIC' ,regression='c')
        p_valor = adfTest[1]   # p_valor
    
    # p_valor = 0.001 # debug
        
    return p_valor
    
###################################################################################################################################
###################################################################################################################################

def retorna_df_AB_ou_BA(str_AB_BA, lst_X,lst_Y):
    
    # é AB
    if str_AB_BA == "AB":  
    
        X_ind = pd.DataFrame( { 'X1' : lst_X  })
        Y_dep = pd.DataFrame( { 'Y'  : lst_Y  })                         
    # é BA
    elif str_AB_BA == "BA":
    
        X_ind = pd.DataFrame( { 'X1' : lst_Y  })
        Y_dep = pd.DataFrame( { 'Y'  : lst_X  })        
    else:
        print("ERRO!! str_AB_BA está com valor inválido!! :" + str_AB_BA )
        sys.quit()
    return X_ind,Y_dep

###################################################################################################################################
###################################################################################################################################

def calula_valor_ls_horizontalidade(numer, denom, criterio, nPeriodo):
    
    list_num = numer["Fechamento"].tolist()  
    list_den = denom["Fechamento"].tolist()  
    
    ratio = [x/y for x, y in zip(list_num, list_den)]
    df_ratio = pd.DataFrame(ratio, columns = ['Ratio']) 
  
    # reverto a serie no calculo [::-1]], senao ele desconsidera os nPeriodo rows mais atuais            
    df_ratio['ratio_mean'] = df_ratio['Ratio'][::-1].rolling(window = nPeriodo).mean()
    
    last_ratio_mean = str( round( df_ratio['ratio_mean'][0],4))
    last_ratio_mean = last_ratio_mean.replace('.',',')
    
    # reverto a serie no calculo [::-1]], senao ele desconsidera os nPeriodoS rows mais atuais
    df_ratio['ratio_std' ] = df_ratio['Ratio'][::-1].rolling(window = nPeriodo).std()
    
    df_ratio['1x_upper_band'] = df_ratio['ratio_mean'] + (df_ratio['ratio_std'] * 2)
    df_ratio['1x_lower_band'] = df_ratio['ratio_mean'] - (df_ratio['ratio_std'] * 2)               
 
    df_UL = df_ratio.head(nPeriodo) 
    
    lst_1x_upper_band = df_UL['1x_upper_band'].tolist()
    lst_1x_lower_band = df_UL['1x_lower_band'].tolist()            
  
    #U = np.mean(lst_1x_upper_band)
    #L = np.mean(lst_1x_lower_band)
    soma_erro_U = 0
    soma_erro_L = 0
    
    if CTE.HORIZ_CRITERIO == CTE.HORIZ_DISP_RELAT:
        
        soma_disp_relat_u =  ( (np.std(lst_1x_upper_band )/np.mean(lst_1x_upper_band) )*100 )**2
              
        soma_disp_relat_l = ( (np.std(lst_1x_lower_band )/np.mean(lst_1x_lower_band) )*100 )**2
               
        return round(math.sqrt(soma_disp_relat_u + soma_disp_relat_l),4)/nPeriodo   
    
    if CTE.HORIZ_CRITERIO == CTE.HORIZ_LAST_VALUE:
        # calcula o erro associado ao nivel inicial da banda de bollinger
        U = lst_1x_upper_band[0]
        L  =lst_1x_lower_band[0]        
                   
    elif CTE.HORIZ_CRITERIO == CTE.HORIZ_FIRST_VALUE:
        U = lst_1x_upper_band[nPeriodo-1]
        L  =lst_1x_lower_band[nPeriodo-1]  
        
    elif CTE.HORIZ_CRITERIO == CTE.HORIZ_MEAN_VALUE:
        U = np.mean(lst_1x_upper_band )
        L = np.mean(lst_1x_lower_band )
        
    for idx in range(1, len(lst_1x_upper_band) -1):
        soma_erro_U  = soma_erro_U + abs( (U - lst_1x_upper_band[idx])/U )
        
    for idx in range(1, len(lst_1x_lower_band) -1):               
        soma_erro_L  = soma_erro_L  + abs( (L - lst_1x_lower_band[idx])/L )                  

    return round(soma_erro_U +soma_erro_L,4)/nPeriodo    

def computa_ls_horizontalidade(dict_preco_full: dict, file_relat):
    
    dict_cpy = dict_preco_full.copy()
    
    dict_ativos_precos_Hor = {}
        
    par_ativos=[]
    
    for kx_ativo, vx_preco in sorted(dict_preco_full.items()):
        
        ############################################
        # remove ativo do loop primario do loop secundario
        ############################################
        
        dict_cpy.pop(kx_ativo, None)

        for ky_ativo, vy_preco in sorted(dict_cpy.items()):

            ###### 
            #  AB
            ###### 
                       
            numer = dict_preco_full[ kx_ativo ]
            denom = dict_preco_full[ ky_ativo ]
             
            soma_erro_AB =  calula_valor_ls_horizontalidade(numer, denom, CTE.HORIZ_CRITERIO)                
 
            ######
            #  BA
            ######          
            
            numer = dict_preco_full[ ky_ativo ]
            denom = dict_preco_full[ kx_ativo ]

            soma_erro_BA =  calula_valor_ls_horizontalidade(numer, denom, CTE.HORIZ_CRITERIO)                
      
            #####################################################
            # IDENTIFICA OS PARES E CRIA NOVO DICTIONARIO
            # LIMITE SUPERIOR É 6,2
            #####################################################
            
            if abs(soma_erro_BA) <= CTE.LIMIAR_HORZ and abs(soma_erro_AB) <= CTE.LIMIAR_HORZ:
                # se não existe, adiciona ativos...
                if not kx_ativo in dict_ativos_precos_Hor:
                    #print("SELECIONANDO ATIVO ["+ kx_ativo + "]..." )  # debug                       
                    print("SELECIONANDO ATIVO ["+ kx_ativo + "]...", file=file_relat)
                    dict_ativos_precos_Hor[ kx_ativo ] = vx_preco
                if not ky_ativo in dict_ativos_precos_Hor:                 
                    dict_ativos_precos_Hor[ ky_ativo ] = vy_preco
                    #print("SELECIONANDO ATIVO ["+ ky_ativo + "]...")   # debug                      
                    print("SELECIONANDO ATIVO ["+ ky_ativo + "]...", file=file_relat)
               
                par_ativos.append( [kx_ativo,ky_ativo] )  
                
                #print("HORIZONTALIDADE BANDAS DE BOLLINGER ATIVOS [" + kx_ativo +"] E [" + ky_ativo +"] VALOR : "+str(min(soma_erro_BA,soma_erro_AB)) +"...")  # debug                
                print("HORIZONTALIDADE BANDAS DE BOLLINGER ATIVOS [" + kx_ativo +"] E [" + ky_ativo +"] VALOR : "+str(min(soma_erro_BA,soma_erro_AB)) +"...", file=file_relat)                
                               

    return dict_ativos_precos_Hor, par_ativos



###################################################################################################################################
#                                                                                                                                 #
########################################  INICIO DO PROGRAMA   ####################################################################
#                                                                                                                                 #
###################################################################################################################################

print(" ---------- Versão do Script LS: V. - 2.4 28.10.2020 ----------")
str_path_hist = "C:\\Users\\rgiovann\\OneDrive\\AULAS\Bagozzi\\PYTHON_SOURCE\\FINANCAS_QUANTITATIVAS\\Database_Python\\"
str_path_out_logs = "C:\\Users\\rgiovann\\OneDrive\\AULAS\Bagozzi\\PYTHON_SOURCE\\FINANCAS_QUANTITATIVAS\\LOGS\\"
file_relat = open(str_path_out_logs + "log_longshort_db_from_tryd_" + datetime.datetime.now().strftime('%Y_%d_%m_%H_%M_%S') + ".txt", "a")

dict_ativos_precos = util.le_historico_ativos(str_path_hist,str_path_out_logs,file_relat)

if dict_ativos_precos:
    print("Calculando cointegração dos pares selecionados...Quantidade ativos selecionados : " +
          str(len(dict_ativos_precos)) )  
    computa_ls_cointegracao(dict_ativos_precos,file_relat)     

print("\n")
print("Fim da execução do script, verifique os resultados no log gerado em arquivo...")
file_relat.close()

##############################################################################################

# debug
# data = [ ["07/04/2020", 15.60], ["06/04/2020" , 15.80 ],["03/04/2020" , 14.10],[ "02/04/2020"  , 14.61] ]
# ativo_python = pd.DataFrame(data,columns = ["Data", "Fechamento"])
