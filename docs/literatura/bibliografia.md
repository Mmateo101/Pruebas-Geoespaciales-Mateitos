# Bibliografía: pasos peatonales, imágenes y muertes de peatones

Búsqueda en OpenAlex (noviembre de 2026) con `scripts/openalex_search.py`. Resultados completos: `openalex_raw.json` (204 trabajos, 6 temas). Esta es la selección curada. Las citas son las de OpenAlex en la fecha de búsqueda.

## 1. Detección de pasos peatonales en imagen aérea o satelital

| Trabajo | Año | Qué aporta |
|---|---|---|
| Berriel et al., *Deep Learning-Based Large-Scale Automatic Satellite Crosswalk Classification*, IEEE GRSL — [doi](https://doi.org/10.1109/LGRS.2017.2719863) / [arXiv](https://arxiv.org/abs/1706.09302) | 2017 | ~250k imágenes, etiquetas de OSM, 97 % de precisión. Clasifica teselas, no localiza. |
| Berriel et al., *Automatic large-scale data acquisition via crowdsourcing for crosswalk classification*, Computers & Graphics — [arXiv](https://arxiv.org/abs/1805.11970) | 2017 | Etiquetas automáticas de OSM + Street View. |
| *Crosswalk Detection from Satellite Imagery for Pedestrian Network Completion*, TRR — [doi](https://doi.org/10.1177/03611981231210545) | 2023 | YOLOv5 en 4 ciudades de Norteamérica (usó imágenes de Google Maps). |
| *CrosswalkNet*, arXiv — [arXiv](https://arxiv.org/abs/2506.07885) | 2025 | Cajas orientadas en ortofotos de 15 cm; 96.5 % precisión, 93.3 % recall. |
| *A two-stage detection and segmentation framework for pedestrian crosswalk inventory and condition assessment from aerial imagery*, Eng. Appl. of AI — [doi](https://doi.org/10.1016/j.engappai.2026.115851) | 2026 | Detección + **estado** del paso (pintura). Lo más cercano a "¿cómo está el paso?". |
| *Automated GIS-Based Framework for Detecting Crosswalk Changes from Bi-Temporal High-Resolution Aerial Images*, TRR — [doi](https://doi.org/10.1177/03611981241292333) | 2024 | Cambios en el tiempo: si un paso se pintó o se borró. |
| *A Dual-Perspective Deep Learning Method for Automated Detection of Occluded Crosswalks from Aerial Imagery*, SSRN — [doi](https://doi.org/10.2139/ssrn.4061399) | 2022 | Pasos tapados por árboles o autos. |
| *End-to-End Deep Structured Models for Drawing Crosswalks*, ECCV (LNCS) — [doi](https://doi.org/10.1007/978-3-030-01258-8_25) | 2018 | Dibuja el polígono del paso. |
| *Extraction and spatial differentiation analysis of urban pedestrian crossings based on high-resolution remote sensing imagery*, SPIE — [doi](https://doi.org/10.1117/12.3118421) | 2026 | Extracción + desigualdad espacial de pasos entre zonas de una ciudad. |
| *Scaling pedestrian crossing analysis to 100 U.S. cities via AI-based segmentation of satellite imagery*, JTLU — [link](https://jtlu.org/index.php/jtlu/article/view/2771/1839) | 2026 | SAM sobre satélite para medir distancia de cruce en 100 ciudades. |
| *Multiscale Analysis of Pedestrian Crossing Distance*, JAPA | 2024 | Distancia de cruce como variable de riesgo. |
| Bühler y Kurath, *Extraction of Crosswalks from Aerial Images* — [OST](https://eprints.ost.ch/id/eprint/485/) | 2015 | Ortofotos suizas, código abierto. |
| *OpenStreetMap: Challenges and Opportunities in ML and Remote Sensing*, IEEE GRSM | 2020 | Calidad de OSM como fuente de etiquetas. |

## 2. Imagen satelital o aérea y riesgo de choque

| Trabajo | Año | Qué aporta |
|---|---|---|
| Najjar et al., *Combining Satellite Imagery and Open Data to Map Road Safety*, AAAI — [doi](https://doi.org/10.1609/aaai.v31i1.11168) | 2017 | Primer mapa de riesgo vial solo con satélite. |
| *Identifying safe intersection design through unsupervised feature extraction from satellite imagery*, CACAIE — [doi](https://doi.org/10.1111/mice.12623) | 2020 | ~900k intersecciones de Australia; diseño de la intersección y choques. Muy relevante. |
| *Unveiling Roadway Hazards: Fatal Crash Risk Estimation Through Multiscale Satellite Imagery and Self-Supervised Learning*, IEEE JSTARS | 2023 | Riesgo de choque fatal solo con satélite. |
| *Beta Distribution Learning for Reliable Roadway Crash Risk Assessment*, AAAI — [arXiv](https://arxiv.org/abs/2511.04886) | 2026 | Riesgo fatal con incertidumbre (distribución, no un punto). |
| *Utilizing High Resolution Satellite Imagery for Automated Road Infrastructure Safety Assessments*, Sensors — [doi](https://doi.org/10.3390/s23094405) | 2023 | YOLO sobre Pléiades Neo (30 cm): 4 clases de pasos, rutas escolares. Útil para saber qué resolución satelital sirve. |
| *Alcohol outlets and firearm violence: a place-based case–control study using satellite imagery and ML*, Injury Prevention | 2019 | Diseño caso-control de lugares con imagen satelital (otro tema, mismo método). |

## 3. Imagen a nivel de calle y atropellamientos

| Trabajo | Año | Qué aporta |
|---|---|---|
| *STRIDE: Street View-based Environmental Feature Detection and Pedestrian Collision Prediction*, ICCV-W — [arXiv](https://arxiv.org/abs/2308.13183) | 2023 | Bogotá: 18k panorámicas, 27 clases, predicción de atropellamientos. |
| *Road Traffic Injuries and the Built Environment in Bogotá, Colombia, 2015–2019*, J. Urban Health | 2024 | Versión epidemiológica del trabajo de Bogotá. |
| *Investigating the influence of streetscape environmental characteristics on pedestrian crashes at intersections using street view images and explainable ML*, AAP — [doi](https://doi.org/10.1016/j.aap.2024.107693) | 2024 | Intersecciones + SHAP. |
| *Leveraging computer vision for predicting collision risks: fatal collisions in the USA 2019–2021*, Injury Prevention — [doi](https://doi.org/10.1136/ip-2023-045153) | 2024 | Street View a nivel nacional, choques fatales. |
| *Exploring fatal/severe pedestrian injury crash frequency at school zone crash hotspots*, J. Transport Geography | 2024 | ML interpretable con imagen de calle. |
| *Street view imagery-based built environment auditing tools: a systematic review*, IJGIS | 2024 | Revisión de métodos de auditoría con imagen. |

## 4. Muertes de peatones y entorno construido (diseño del estudio)

| Trabajo | Año | Qué aporta |
|---|---|---|
| *Design of a location-based case-control study of built-environment risk factors for pedestrian fatalities in the United States*, Am. J. Epidemiology — [doi](https://doi.org/10.1093/aje/kwae377) | 2024 | **El diseño metodológico a seguir**: lugares con muertes vs. lugares control emparejados. |
| Chang et al., *Predicting effects of built environment on fatal pedestrian accidents at location-specific level: XGBoost and SHAP*, AAP | 2022 | Corea: 13k lugares fatales vs. 134k controles. |
| *Examining Risk Factors Influencing Fatal Pedestrian Crashes on Rural Highways: Matched Case-Control*, TRR — [doi](https://doi.org/10.1177/03611981261431736) | 2026 | Caso-control emparejado en un país de ingreso medio (India). |
| *A comprehensive study on identification of risk factors for fatal pedestrian crashes at urban intersections*, Asian Transport Studies | 2020 | Factores de riesgo en intersecciones urbanas. |
| *Pedestrian injury and the built environment: an environmental scan of hotspots*, BMC Public Health | 2009 | Auditoría de puntos críticos. |
| *Crossing Locations, Light Conditions, and Pedestrian Injury Severity*, TRR | 2006 | Ubicación del cruce y gravedad. |

## 5. Efecto de los pasos marcados

| Trabajo | Año | Qué aporta |
|---|---|---|
| Zegeer et al., *Safety Effects of Marked versus Unmarked Crosswalks at Uncontrolled Locations*, FHWA | 2005 | Referencia clásica: en vías anchas y rápidas, pintar el paso sin otras medidas no reduce (e incluso aumenta) los atropellamientos. Clave para interpretar resultados. |
| *Marked-Crosswalk Dilemma*, TRR | 2008 | El debate de 35 años sobre pasos marcados. |
| *Association between Roadway Intersection Characteristics and Pedestrian Crash Risk in Alameda County*, TRR | 2010 | Características de intersección y riesgo. |
| *Pedestrian–Vehicle Interaction at Unsignalized Crosswalks: A Systematic Review*, Sustainability | 2020 | Revisión sistemática. |

## 6. México y Latinoamérica

| Trabajo | Año | Qué aporta |
|---|---|---|
| Cárdenas-Cárdenas et al., *One-year impact of a multicomponent, street-level design intervention in Mexico City on pedestrian crashes* (Pasos Seguros), JECH | 2022 | Intervenciones en intersecciones de CDMX: −21 % atropellamientos. Usa datos del C5. |
| *Propuesta de un índice de seguridad de cruces peatonales para la Ciudad de México*, Rev. Panam. Salud Pública — [doi](https://doi.org/10.26633/rpsp.2019.6) | 2019 | **Índice de calidad de cruces en CDMX comparado con accidentes.** Auditoría manual: lo que tu pipeline podría automatizar. |
| *Un estudio general sobre colisiones peatonales y su fatalidad en Ciudad de México, 2004–2015*, Rev. Transporte y Territorio — [doi](https://doi.org/10.34096/rtt.i23.9660) | 2020 | Modelos de frecuencia y fatalidad en CDMX. |
| *Letalidad peatonal en Ciudad de México: perspectiva de racionalidad limitada* — [doi](https://doi.org/10.47386/vol1num1art5_21) | 2021 | Letalidad 1997–2017; intersecciones vs. no intersecciones. |
| *Analysis of fatal pedestrian injuries in Mexico City, 1994–1997*, Injury | 2001 | Antecedente histórico. |
| *Comparación de datos sobre mortalidad por atropellamientos en la Ciudad de México*, Salud Pública de México | 2011 | Calidad de las fuentes de datos de muertes. |
| *Motivos de uso y no uso de puentes peatonales en la Ciudad de México*, Salud Pública de México | 2010 | Puentes peatonales: alternativa al paso a nivel. |
| *Relación cuantitativa entre atropellamientos y puentes peatonales en Chihuahua*, Revista INVI | 2022 | Puentes peatonales y atropellamientos. |
| *Utilidad del análisis geográfico en el estudio de las muertes por atropellamiento*, Salud Pública de México | 2000 | Análisis espacial de muertes. |
| *The urban structure and pedestrian injuries: typological analysis in Hermosillo*, Traffic Injury Prevention | 2023 | Tipología urbana en México. |
| *Urban landscape and street-design factors associated with road-traffic mortality in Latin America (SALURBAL)*, Lancet Planetary Health — [doi](https://doi.org/10.1016/s2542-5196(21)00323-5) | 2022 | Escala ciudad, incluye México. |

## Hueco identificado

No apareció ningún trabajo que use **imagen aérea o satelital con visión por computadora** para caracterizar los cruces **donde mueren peatones en México**. Los más cercanos:
- el índice de seguridad de cruces de CDMX (2019), con auditoría manual;
- Pasos Seguros (2022), que evalúa intervenciones, no imagen;
- STRIDE (Bogotá), con imagen a nivel de calle, no aérea.

Antes de afirmarlo en una publicación conviene confirmarlo en Scopus/Web of Science.
