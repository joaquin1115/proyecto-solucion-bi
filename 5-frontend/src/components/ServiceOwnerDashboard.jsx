// frontend/src/components/ServiceOwnerDashboard.jsx
import React, { useState, useEffect } from 'react';
import ServiceOwnerLineChart from './ServiceOwnerLineChart';
import ServiceOwnerRadarChart from './ServiceOwnerRadarChart';
import GaugeChart from './GaugeChart';
import { API_BASE_URL } from '../config';

function ServiceOwnerDashboard() {
  const [filters, setFilters] = useState(() => {
    const saved = localStorage.getItem('serviceOwnerDashboardFilters');
    return saved
      ? JSON.parse(saved)
      : { maturityLevel: 'practitioner', geography: 'todos', service1_name: 'todos' };
  });

  const [selectedMetric, setSelectedMetric] = useState('adopcion_total_pct');
  const [chartView, setChartView] = useState('monthly');

  const practitionerMetricLabels = {
    adopcion_total_pct: 'Adopción Total',
    rfo_ok_pct: 'RFO OK',
    dep_pct: 'DEP',
    adopcion_sn2_pct: 'Adopción SN2',
    calidad_features_pct: 'Calidad Features',
    seguridad_pct: 'Seguridad',
  };

  const ciMetricLabels = {
    adopcion_total_pct: 'Adopción Total',
    analisis_review_7dias_pct: 'Análisis Review 7 Días',
    historias_fix_version_pct: 'Historias Fix Version',
    repos_nomenclatura_pct: 'Repos Nomenclatura',
    aprobacion_pr_pct: 'Aprobación PR',
    tamano_pr_pct: 'Tamaño PR',
    repos_chimera_pct: 'Repos Chimera',
    tiempo_integracion_pct: 'Tiempo Integración',
    tiempo_construcciones_pct: 'Tiempo Construcciones',
    construcciones_correctas_pct: 'Construcciones Correctas',
    tiempo_arreglar_construcciones_pct: 'Tiempo Arreglar Construcciones',
    calidad_codigo_pct: 'Calidad Código',
    items_pruebas_xray_pct: 'Pruebas Xray',
  };

  const practitionerRadarMetricLabels = {
    rfo_ok_pct: 'RFO OK',
    dep_pct: 'DEP',
    adopcion_sn2_pct: 'Adopción SN2',
    calidad_features_pct: 'Calidad Features',
    seguridad_pct: 'Seguridad',
  };

  const ciRadarMetricLabels = {
    analisis_review_7dias_pct: 'Análisis Review 7 Días',
    historias_fix_version_pct: 'Historias Fix Version',
    repos_nomenclatura_pct: 'Repos Nomenclatura',
    aprobacion_pr_pct: 'Aprobación PR',
    tamano_pr_pct: 'Tamaño PR',
    repos_chimera_pct: 'Repos Chimera',
    tiempo_integracion_pct: 'Tiempo Integración',
    tiempo_construcciones_pct: 'Tiempo Construcciones',
    construcciones_correctas_pct: 'Construcciones Correctas',
    tiempo_arreglar_construcciones_pct: 'Tiempo Arreglar Construcciones',
    calidad_codigo_pct: 'Calidad Código',
    items_pruebas_xray_pct: 'Pruebas Xray',
  };

  const [geographies, setGeographies] = useState([]);
  const [services, setServices] = useState([]);

  const [loadingGeographies, setLoadingGeographies] = useState(false);
  const [loadingServices, setLoadingServices] = useState(false);

  const [practitionerChartData, setPractitionerChartData] = useState([]);
  const [ciChartData, setCiChartData] = useState([]);

  const [loadingChart, setLoadingChart] = useState(false);
  const [latestAdoption, setLatestAdoption] = useState(null);

  const [kpiData, setKpiData] = useState(null);
  const [loadingKpis, setLoadingKpis] = useState(false);

  const [availableDates, setAvailableDates] = useState([]);
  const [compareDate, setCompareDate] = useState('');
  const [kpiCompareData, setKpiCompareData] = useState(null);
  const [loadingCompareKpis, setLoadingCompareKpis] = useState(false);

  const isInitialMount = React.useRef(true);

  /* ==========================================================
     1. FETCH GEOGRAPHIES
  ========================================================== */
  useEffect(() => {
    const fetchGeos = async () => {
      if (filters.maturityLevel === 'todos') {
        setGeographies([]);
        return;
      }

      setLoadingGeographies(true);

      try {
        const res = await fetch(
          `${API_BASE_URL}/api/service-owner/geographies?maturity_level=${filters.maturityLevel}`
        );
        if (!res.ok) throw new Error();
        const json = await res.json();
        setGeographies(json.geografias || []);
      } catch {
        setGeographies([]);
      } finally {
        setLoadingGeographies(false);
      }
    };

    fetchGeos();

    if (!isInitialMount.current) {
      setFilters((f) => ({ ...f, geography: 'todos', service1_name: 'todos' }));
      setServices([]);
    }
  }, [filters.maturityLevel]);

  /* ==========================================================
     2. FETCH SERVICES
  ========================================================== */
  useEffect(() => {
    const fetchServicesFn = async () => {
      if (filters.geography === 'todos') {
        setServices([]);
        return;
      }

      setLoadingServices(true);
      try {
        const params = new URLSearchParams({
          maturity_level: filters.maturityLevel,
          geography: filters.geography,
        });

        const res = await fetch(`${API_BASE_URL}/api/service-owner/services?${params}`);
        if (!res.ok) throw new Error();
        const json = await res.json();
        setServices(json.services || []);
      } catch {
        setServices([]);
      } finally {
        setLoadingServices(false);
      }
    };

    fetchServicesFn();

    if (!isInitialMount.current) {
      setFilters((f) => ({ ...f, service1_name: 'todos' }));
      setPractitionerChartData([]);
      setCiChartData([]);
      setKpiData(null);
      setAvailableDates([]);
    }
  }, [filters.maturityLevel, filters.geography]);

  /* ==========================================================
     3. FETCH CHART DATA
  ========================================================== */
  useEffect(() => {
    const fetchChartData = async () => {
      if (filters.service1_name === 'todos') {
        setLatestAdoption(null);
        setPractitionerChartData([]);
        setCiChartData([]);
        return;
      }

      setLoadingChart(true);

      try {
        const params = new URLSearchParams({
          maturity_level: filters.maturityLevel,
          geography: filters.geography,
          service1_name: filters.service1_name,
          metric: selectedMetric,
        });

        const res = await fetch(`${API_BASE_URL}/api/service-owner/chart?${params}`);
        if (!res.ok) throw new Error('Error fetch chart');
        const json = await res.json();

        if (!json || json.length === 0) {
          setLatestAdoption(null);
        } else {
          setLatestAdoption(json[json.length - 1] || null);
        }

        if (filters.maturityLevel === 'practitioner') {
          setPractitionerChartData(json || []);
        } else {
          setCiChartData(json || []);
        }
      } catch {
        setLatestAdoption(null);
        setPractitionerChartData([]);
        setCiChartData([]);
      } finally {
        setLoadingChart(false);
      }
    };

    fetchChartData();
  }, [filters.maturityLevel, filters.geography, filters.service1_name, selectedMetric]);

  /* ==========================================================
     4. KPI DATA + DATES
  ========================================================== */
  useEffect(() => {
    const fetchKpis = async () => {
      if (filters.service1_name === 'todos' || filters.geography === 'todos') {
        setKpiData(null);
        setAvailableDates([]);
        return;
      }

      setLoadingKpis(true);

      try {
        const params = new URLSearchParams({
          maturity_level: filters.maturityLevel,
          geography: filters.geography,
          service1_name: filters.service1_name,
        });

        const [kpiRes, dateRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/service-owner/service-kpis?${params}`),
          fetch(`${API_BASE_URL}/api/service-owner/kpi-dates?${params}`),
        ]);

        let kpiJson = null;
        let dateJson = [];

        if (kpiRes.ok) kpiJson = await kpiRes.json();
        if (dateRes.ok) dateJson = await dateRes.json();

        setKpiData(kpiJson);
        setAvailableDates(dateJson || []);
      } catch {
        setKpiData(null);
        setAvailableDates([]);
      } finally {
        setLoadingKpis(false);
      }
    };

    fetchKpis();
  }, [filters.maturityLevel, filters.geography, filters.service1_name]);

  /* ==========================================================
     5. KPI COMPARISON
  ========================================================== */
  useEffect(() => {
    const fetchCompare = async () => {
      if (!compareDate) {
        setKpiCompareData(null);
        return;
      }

      setLoadingCompareKpis(true);

      try {
        const params = new URLSearchParams({
          maturity_level: filters.maturityLevel,
          geography: filters.geography,
          service1_name: filters.service1_name,
          date: compareDate,
        });

        const res = await fetch(`${API_BASE_URL}/api/service-owner/service-kpis?${params}`);
        if (!res.ok) throw new Error();
        const json = await res.json();
        setKpiCompareData(json);
      } catch {
        setKpiCompareData(null);
      } finally {
        setLoadingCompareKpis(false);
      }
    };

    fetchCompare();
  }, [compareDate]);

  /* ==========================================================
     6. SAVE FILTERS
  ========================================================== */
  useEffect(() => {
    localStorage.setItem('serviceOwnerDashboardFilters', JSON.stringify(filters));
  }, [filters]);

  useEffect(() => {
    isInitialMount.current = false;
  }, []);

  /* ==========================================================
     HANDLERS
  ========================================================== */
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
    setCompareDate('');
  };

  const handleMaturityLevelChange = (level) => {
    setFilters({
      maturityLevel: level,
      geography: 'todos',
      service1_name: 'todos',
    });
    setSelectedMetric('adopcion_total_pct');
    setCompareDate('');
    setKpiCompareData(null);
  };

  /* ==========================================================
     RENDER
  ========================================================== */
  return (
    <div>
      <h2 className="font-orbitron text-2xl font-bold text-white mb-4">Filtros Service Owner</h2>

      {/* --------------------------------------------
          FILTROS PRINCIPALES
      --------------------------------------------- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-6 bg-primary/5 border border-primary/20 rounded-lg">
        {/* Maturity Level */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-primary uppercase tracking-wider">
            Nivel de Madurez
          </label>
          <select
            name="maturityLevel"
            value={filters.maturityLevel}
            onChange={(e) => handleMaturityLevelChange(e.target.value)}
            className="form-select w-full h-12 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg"
          >
            <option value="practitioner">Practitioner</option>
            <option value="continuous_integration">Continuous Integration</option>
          </select>
        </div>

        {/* Geography */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-primary uppercase tracking-wider">
            Geografía
          </label>

          <select
            name="geography"
            value={filters.geography}
            onChange={handleFilterChange}
            disabled={loadingGeographies}
            className="form-select w-full h-12 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg disabled:opacity-50"
          >
            <option value="todos">Todas</option>
            {geographies.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        {/* Service */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-primary uppercase tracking-wider">
            Servicio N1
          </label>

          <select
            name="service1_name"
            value={filters.service1_name}
            onChange={handleFilterChange}
            disabled={loadingServices}
            className="form-select w-full h-12 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg disabled:opacity-50"
          >
            <option value="todos">Todos</option>
            {services.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* --------------------------------------------
          SI NO HAY SERVICIO SELECCIONADO
      --------------------------------------------- */}
      {filters.service1_name === 'todos' ? (
        <div className="flex flex-col items-center justify-center h-64 bg-primary/5 border border-primary/20 rounded-lg p-8">
          <span className="material-symbols-outlined text-6xl text-primary/50 mb-4">
            checklist
          </span>
          <h2 className="font-orbitron text-2xl font-bold text-white mb-2">
            Selecciona un Servicio
          </h2>
          <p className="font-mono text-white/70 text-center">
            Por favor, selecciona una geografía y un servicio N1 para ver los datos.
          </p>
        </div>
      ) : (
        <>
          {/* --------------------------------------------
              LINE CHART + KPI PANEL
          --------------------------------------------- */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            <div className="lg:col-span-2 rounded-lg border border-primary/20 bg-primary/5 p-6">
              <div className="flex flex-col sm:flex-row justify-between mb-4">
                <h3 className="font-orbitron text-xl font-bold text-white">
                  {`Evolución de ${
                    (filters.maturityLevel === 'practitioner'
                      ? practitionerMetricLabels
                      : ciMetricLabels)[selectedMetric]
                  }`}
                </h3>

                <div className="flex gap-2">
                  <button
                    onClick={() => setChartView('monthly')}
                    className={`px-3 py-1 text-xs font-bold rounded-md ${
                      chartView === 'monthly'
                        ? 'bg-primary text-white'
                        : 'bg-primary/20 text-white/70 hover:bg-primary/30'
                    }`}
                  >
                    MENSUAL
                  </button>

                  <button
                    onClick={() => setChartView('cumulative')}
                    className={`px-3 py-1 text-xs font-bold rounded-md ${
                      chartView === 'cumulative'
                        ? 'bg-primary text-white'
                        : 'bg-primary/20 text-white/70 hover:bg-primary/30'
                    }`}
                  >
                    ACUMULADO
                  </button>
                </div>
              </div>

              {loadingChart ? (
                <div className="flex justify-center items-center h-64 text-white/70">
                  Cargando gráfico...
                </div>
              ) : (
                <ServiceOwnerLineChart
                  data={
                    chartView === 'cumulative'
                      ? (filters.maturityLevel === 'practitioner'
                          ? practitionerChartData
                          : ciChartData
                        ).map((item, idx, arr) => {
                          const slice = arr.slice(0, idx + 1);
                          const average =
                            slice.reduce(
                              (acc, v) => acc + parseFloat(v.avg_adoption),
                              0
                            ) / slice.length;

                          return {
                            ...item,
                            avg_adoption: average,
                          };
                        })
                      : filters.maturityLevel === 'practitioner'
                      ? practitionerChartData
                      : ciChartData
                  }
                  chartType={chartView === 'cumulative' ? 'area' : 'line'}
                />
              )}
            </div>

            {/* KPI PANEL */}
            <div className="flex flex-col items-center justify-center gap-4 rounded-lg bg-primary/5 border border-primary/20 p-6">
              {loadingChart ? (
                <div className="flex items-center justify-center h-full text-white/70">
                  Cargando...
                </div>
              ) : latestAdoption ? (
                selectedMetric === 'adopcion_total_pct' ? (
                  <GaugeChart value={parseFloat(latestAdoption.avg_adoption || 0)} />
                ) : (
                  <div className="flex flex-col items-center">
                    <span className="font-orbitron text-4xl font-bold text-white">
                      {parseFloat(latestAdoption.avg_adoption || 0).toFixed(2)}%
                    </span>
                    <span className="font-mono text-sm text-primary uppercase mt-2">
                      {(filters.maturityLevel === 'practitioner'
                        ? practitionerMetricLabels
                        : ciMetricLabels)[selectedMetric]}
                    </span>
                  </div>
                )
              ) : (
                <p className="font-orbitron text-3xl font-bold text-white">N/A</p>
              )}
            </div>
          </section>

          {/* --------------------------------------------
              BOTONES DE MÉTRICAS
          --------------------------------------------- */}
          {filters.maturityLevel === 'practitioner' ? (
            <div className="mt-6 p-6 bg-primary/5 border border-primary/20 rounded-lg">
              <h3 className="font-orbitron text-xl font-bold text-white mb-4">
                KPI's Practitioner
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                {Object.entries(practitionerMetricLabels).map(([k, v]) => (
                  <button
                    key={k}
                    onClick={() => setSelectedMetric(k)}
                    className={`px-3 py-2 text-xs font-bold rounded-lg ${
                      selectedMetric === k
                        ? 'bg-primary text-white shadow-glow-primary'
                        : 'bg-primary/20 text-white/70 hover:bg-primary/30'
                    }`}
                  >
                    {v.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mt-6 p-6 bg-primary/5 border border-primary/20 rounded-lg">
              <h3 className="font-orbitron text-xl font-bold text-white mb-4">
                KPI's Continuous Integration
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-2">
                {Object.entries(ciMetricLabels).map(([k, v]) => (
                  <button
                    key={k}
                    onClick={() => setSelectedMetric(k)}
                    className={`px-3 py-2 text-xs font-bold rounded-lg ${
                      selectedMetric === k
                        ? 'bg-primary text-white shadow-glow-primary'
                        : 'bg-primary/20 text-white/70 hover:bg-primary/30'
                    }`}
                  >
                    {v.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* --------------------------------------------
              RADAR KPI CHART
          --------------------------------------------- */}
          <div className="mt-6 p-6 bg-primary/5 border border-primary/20 rounded-lg">
            <h3 className="font-orbitron text-xl font-bold text-white mb-4">
              Análisis Radar de KPIs
              {kpiData && kpiData.month_label && ` - ${kpiData.month_label}`}
              {kpiCompareData && kpiCompareData.month_label && ` vs ${kpiCompareData.month_label}`}
            </h3>

            <div className="flex flex-col md:flex-row gap-4">
              {/* Radar */}
              <div className="w-full md:w-3/4">
                {loadingKpis || loadingCompareKpis ? (
                  <div className="flex items-center justify-center h-96 text-white/70">
                    Cargando...
                  </div>
                ) : kpiData ? (
                  <div style={{ width: '100%', height: '400px' }}>
                    <ServiceOwnerRadarChart
                      data={kpiData}
                      compareData={kpiCompareData}
                      metricLabels={
                        filters.maturityLevel === 'practitioner'
                          ? practitionerRadarMetricLabels
                          : ciRadarMetricLabels
                      }
                    />
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-96 text-white/70">
                    No hay datos.
                  </div>
                )}
              </div>

              {/* Compare */}
              {availableDates.length > 1 && (
                <div className="w-full md:w-1/4 flex flex-col justify-start">
                  <label className="block text-sm font-medium text-primary uppercase mb-2">
                    Comparar con:
                  </label>

                  <select
                    value={compareDate}
                    onChange={(e) => setCompareDate(e.target.value)}
                    className="form-select w-full h-10 bg-black/40 border border-primary/30 text-white rounded-lg"
                  >
                    <option value="">No comparar</option>
                    {availableDates.map((d) => (
                      <option key={d.month} value={d.month}>
                        {d.month_label}
                      </option>
                    ))}
                  </select>

                  <div className="font-mono text-sm text-white/80 space-y-3 mt-6">
                    <h4 className="font-orbitron text-base font-bold text-white">
                      Leyenda
                    </h4>

                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 bg-cyan-400 rounded-sm" />
                      <span>{kpiData?.month_label || 'Actual'}</span>
                    </div>

                    {compareDate && (
                      <div className="flex items-center gap-3">
                        <div className="w-4 h-4 bg-purple-400 rounded-sm" />
                        <span>{kpiCompareData?.month_label || 'Comparación'}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ServiceOwnerDashboard;