rm(list=ls())
if (!require("xml2")) install.packages("xml2")
if (!require("rvest")) install.packages("rvest")
library(xml2)
library(rvest)
pasta_entrada <- "C:/Users/conta/OneDrive/Área de Trabalho/teste web/anuncios_html"
pasta_saida   <- "C:/Users/conta/OneDrive/Área de Trabalho/teste web/anuncios_html/txt"
if (!dir.exists(pasta_saida)) {
  dir.create(pasta_saida, recursive = TRUE)
}
arquivos_html <- list.files(path = pasta_entrada, pattern = "\\.html?$", full.names = TRUE)
total <- length(arquivos_html)
pb <- txtProgressBar(min = 0, max = total, style = 3)
for (i in seq_along(arquivos_html)) {
  arquivo <- arquivos_html[i]
  try({
    pagina <- read_html(arquivo)
    texto_extraido <- html_text(pagina, trim = TRUE)
        nome_base <- tools::file_path_sans_ext(basename(arquivo))
    caminho_saida <- file.path(pasta_saida, paste0(nome_base, ".txt"))
        writeLines(texto_extraido, caminho_saida, useBytes = TRUE)
  }, silent = TRUE)
    setTxtProgressBar(pb, i)
}
close(pb)
cat("✅ Extração concluída para", total, "arquivos.\n")





#ler txt e cria data.frame
if (!require("jsonlite")) install.packages("jsonlite")
library(jsonlite)

pasta_txt <- "C:/Users/conta/OneDrive/Área de Trabalho/teste web/anuncios_html/txt"  # Ex: "C:/Users/Adryan/textos"
arquivos <- list.files(pasta_txt, pattern = "\\.txt$", full.names = TRUE)
lista_resultado <- list()
chaves_desejadas <- c("brand", "model", "version", "gearbox", "subject", "region", 
                      "category", "vehicle_model", "cartype", "regdate", 
                      "mileage", "motorpower", "fuel", "doors","price","municipality","sellerName","professionalAd")
extrair_valor <- function(texto, chave) {
  padrao <- paste0('"', chave, '"\\s*:\\s*"?(.*?)"?(,|$)')
  match <- regmatches(texto, regexec(padrao, texto, perl = TRUE))[[1]]
  if (length(match) >= 2) return(trimws(match[2])) else return(NA)
}
for (arquivo in arquivos) {
  linhas <- readLines(arquivo, encoding = "UTF-8", warn = FALSE)
  texto <- paste(linhas, collapse = " ")
  dados <- sapply(chaves_desejadas, function(chave) extrair_valor(texto, chave))
  dados <- c(dados, arquivo_origem = basename(arquivo))
  lista_resultado[[arquivo]] <- as.list(dados)
}
df_final <- do.call(rbind, lapply(lista_resultado, as.data.frame, stringsAsFactors = FALSE))
rownames(df_final) <- NULL
print(df_final)


df_final$price=as.numeric(df_final$price)



library(ggplot2)
library(dplyr)

# Criar uma coluna combinando brand + model
df_final <- df_final %>%
  mutate(grupo = paste(brand, model, sep = " - "))

# Ordenar por média de preço para melhorar a visualização
df_ordenado <- df_final %>%
  group_by(grupo) %>%
  mutate(preco_medio = mean(price)) %>%
  ungroup() %>%
  arrange(preco_medio)

# Reordenar fator
df_ordenado$grupo <- factor(df_ordenado$grupo, levels = unique(df_ordenado$grupo))

# Gráfico
ggplot(df_ordenado, aes(x = grupo, y = price, color = grupo)) +
  geom_point(size = 3, alpha = 0.7) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Preços por Marca e Modelo",
       x = "Marca - Modelo",
       y = "Preço (R$)",
       color = "Grupo")




top_grupos <- df_final %>%
  count(grupo = paste(brand, model)) %>%
  top_n(10, n) %>%
  pull(grupo)

df_filtrado <- df_final %>%
  mutate(grupo = paste(brand, model)) %>%
  filter(grupo %in% top_grupos)


ggplot(df_filtrado, aes(x = grupo, y = price, fill = grupo)) +
  geom_boxplot(alpha = 0.6) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Distribuição de Preços por Grupo",
       x = "Marca - Modelo",
       y = "Preço (R$)",
       fill = "Grupo")




library(plotly)
library(dplyr)

# Criar uma coluna de grupo se ainda não existir
df_ordenado <- df_final %>%
  mutate(grupo = paste(brand, model, sep = " - ")) %>%
  group_by(grupo) %>%
  mutate(preco_medio = mean(price)) %>%
  ungroup() %>%
  arrange(preco_medio)

df_ordenado$grupo <- factor(df_ordenado$grupo, levels = unique(df_ordenado$grupo))

# Gráfico com plotly
plot_ly(df_ordenado,
        x = ~grupo,
        y = ~price,
        type = 'scatter',
        mode = 'markers',
        marker = list(size = 8, opacity = 0.7),
        hoverinfo = 'text',
        text = ~paste("Grupo:", grupo, "<br>Preço: R$", price)) %>%
  layout(title = "Preços por Marca e Modelo",
         xaxis = list(title = "Marca - Modelo",
                      tickangle = -45),
         yaxis = list(title = "Preço (R$)"),
         showlegend = FALSE)
