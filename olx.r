#Consulta ao OLX

#Autor: Adryan Fernandes Rocha de Brito
#data 29/05/2020

#Script para consulta o site do Olx na categoria Motos
#é feito a consulta de preço, nome, local, quilometragem e cilindradas
#além disso é criado um arquivo em .csv em repositorio local para analise 
#posterior. 

#Script ainda em construção

#Inicio

#Limpeza da área de trabalho
rm(list=ls())]

#Bibliotecas utilizadas no script
library(rvest)
library(stringr)
library(dplyr)
library(lubridate)
library(readr)

#definição do objeto que deve receber as informações coletadas
dados=NULL

#loop invertido para consultar informações mais antigas primeiro
for(i in 40:1){
  #donwload de página web referente útima posição
  webpage=read_html(paste0("https://rn.olx.com.br/autos-e-pecas/motos?o=",i))
  #consultas realizadas nesse arquivo baixado
  price=webpage%>%html_nodes(".fnmrjs-16")%>%html_text(trim=T)
  km=str_sub(webpage%>%html_nodes(".jm5s8b-0")%>%html_text(trim=T),
             end=str_locate(webpage%>%html_nodes(".jm5s8b-0")%>%html_text(trim=T),"m")[,1])
  cl=str_sub(webpage%>%html_nodes(".jm5s8b-0")%>%html_text(trim=T),
             start=str_locate(webpage%>%html_nodes(".jm5s8b-0")%>%html_text(trim=T),"[[|]]")[,1]+2)
  nome=webpage%>%html_nodes(".fnmrjs-10")%>%html_text(trim=T)
  local=webpage%>%html_nodes(".fnmrjs-13")%>%html_text(trim=T)
  #união das informações coletadas
  t=data_frame(nome=nome,
               price=price,
               km=km,
               cl=cl,
               local=local)
  #incrementação no arquivo destinado a coleta
  dados=rbind(dados,t)
  #pausa no código de 10 segundos para não sobre carregar o site
  Sys.sleep(10)
}
#backup das informações coletadas
dados1=dados
dados=dados1

#ajuste no separador do preço
dados$price=str_replace(dados$price,fixed("."),"")
dados$price=str_replace(dados$price,fixed("R$")," ")
dados$price=str_trim(dados$price)
dados$price=as.numeric(dados$price)

#ajuste nas informações de cilindradas
dados$cl=str_replace(dados$cl,fixed("Cilindrada: ")," ")
dados$cl=str_trim(dados$cl)

#retirada de repetições
#como o site é atualizado periodicamente é possível que o 
#as informações tenham se repetido durante a coleta
dados=unique(dados)

#escrevendo dados em um arquivo .csv local
write_csv(dados,"oferta de motos na OLX.csv")
