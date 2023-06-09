rm(list=ls())

library(readxl)
library(cowplot)
library(tidyverse)
library(ggpubr)
library(Hmisc)
library(RColorBrewer)


# Correlation #----
library("PerformanceAnalytics")

Cor_data <- read_excel('Radiomics_fat_cor[groupby=muscle].xlsx')%>%mutate_at(c("Fat_fraction", 'original_firstorder_Skewness'), as.numeric)


#chart.Correlation(Refractory_cor, histogram=TRUE, pch=20)

#library(ggstatsplot)
#ggcorrmat(Cor_data, type = "pearson", p.adjust.method="none",ggcorrplot.args = list(insig = "blank"), colors = c("#d6d9db", "#FFFFFF", "#a93522"), lab = TRUE, messages=TRUE, output = "correlations")

library(correlation)

Cor_data$"wavelet-LLH_firstorder_Skewness"

# "wavelet-LLH_firstorder_Skewness" as the most indicator 

ggscatter(Cor_data, x = "Fat_fraction", y = "original_firstorder_Skewness", 
          color = "#3b4992", 
          add = "reg.line", conf.int = TRUE, 
          add.params = list(color = "#ee0000", fill = "lightgray"))


ggplot(Cor_data, aes(x="Fat_fraction", y="original_firstorder_Skewness")) +
  geom_point()

my_palette <- c('#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#92c5de', '#4393c3', '#2166ac', '#053061', '#008b8b')

ggplot(Cor_data, aes(x=Fat_fraction, y=original_firstorder_Skewness, color=Muscle))+
  geom_point()+ 
  geom_smooth(aes(group = 1), method=lm, color = "black")+
  scale_color_manual(values = my_palette)+theme_minimal_grid(12)

lm(Cor_data$Fat_fraction ~ Cor_data$original_firstorder_Skewness)


ggscatter(Cor_data, x = "Fat_fraction", y = "original_firstorder_Skewness", 
          fill  = "Muscle", add = "reg.line", conf.int = TRUE, palette=c('#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7', '#f7f7f7', '#92c5de', '#4393c3', '#2166ac', '#053061', '#008b8b'))


