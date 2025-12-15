// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import PieChart from './PieChart';
import StackedBarChart from './StackedBarChart';
import { API_BASE_URL } from '../config';

function Dashboard() {
  const [data, setData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [filters, setFilters] = useState(() => {
    const saved = localStorage.getItem('globalDashboardFilters');
    return saved ? JSON.parse(saved) : { geografia: 'todos', fecha: 'todos' };
  });

  const [filterOptions, setFilterOptions] = useState({
    geografias: [],
    services: [],
    fechas: [],
  });

  const [pagination, setPagination] = useState({
    currentPage: 1,
    rowsPerPage: 10,
  });

  const [certificationLevels, setCertificationLevels] = useState({
    'LEVEL 3': 0,
    'LEVEL 2': 0,
    'LEVEL 1': 0,
    'no certificado': 0,
  });

  const [geoCertificationData, setGeoCertificationData] = useState([]);

  const [summaryData, setSummaryData] = useState({
    totalCount: 0,
    avg_adoption: 0,
    geographies_count: 0,
  });

  const [maturityLevel, setMaturityLevel] = useState(() => {
    return localStorage.getItem('globalDashboardMaturityLevel') || 'practitioner';
  });

  /* ----------------------------------------------------------------------------------------------
     FETCH PRINCIPAL
  ---------------------------------------------------------------------------------------------- */

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError('');

      try {
        const filterParams = new URLSearchParams({
          maturity_level: maturityLevel,
        });

        // ⭐ REEMPLAZADO: fetch('/api/filters?...')
        const filterOptionsResponse = await fetch(
          `${API_BASE_URL}/api/filters?${filterParams}`
        );

        if (!filterOptionsResponse.ok)
          throw new Error('No se pudieron cargar las opciones de filtro.');

        const filtersResult = await filterOptionsResponse.json();
        setFilterOptions(filtersResult);

        const queryParams = new URLSearchParams({
          maturity_level: maturityLevel,
          page: pagination.currentPage,
          limit: pagination.rowsPerPage,
          geografia: filters.geografia,
          fecha: filters.fecha,
        });

        const chartParams = new URLSearchParams({
          maturity_level: maturityLevel,
          geografia: filters.geografia,
          fecha: filters.fecha,
        });

        const barChartParams = new URLSearchParams({
          maturity_level: maturityLevel,
          fecha: filters.fecha,
        });

        // ⭐ TODOS ESTOS AHORA APUNTAN A TU BACKEND REAL
        const [dataRes, summaryRes, geoRes, summaryDataRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/data?${queryParams}`),
          fetch(`${API_BASE_URL}/api/certification-summary?${chartParams}`),
          fetch(`${API_BASE_URL}/api/certification-by-geography?${barChartParams}`),
          fetch(`${API_BASE_URL}/api/summary?${chartParams}`),
        ]);

        if (!dataRes.ok) {
          const err = await dataRes.json().catch(() => ({}));
          throw new Error(err.error || 'Error al obtener datos de la tabla.');
        }
        if (!summaryRes.ok) throw new Error('Error en resumen.');
        if (!geoRes.ok) throw new Error('Error en certificación por geografía.');
        if (!summaryDataRes.ok) throw new Error('Error en KPIs globales.');

        const tableData = await dataRes.json();
        const certSummary = await summaryRes.json();
        const geoData = await geoRes.json();
        const summaryInfo = await summaryDataRes.json();

        setData(tableData.data || []);
        setTotalCount(tableData.totalCount || 0);
        setCertificationLevels(certSummary || {});
        setGeoCertificationData(geoData || []);
        setSummaryData(summaryInfo || {});
      } catch (err) {
        setError(err.message);
        setData([]);
        setTotalCount(0);
        setCertificationLevels({
          'LEVEL 3': 0,
          'LEVEL 2': 0,
          'LEVEL 1': 0,
          'no certificado': 0,
        });
        setGeoCertificationData([]);
        setSummaryData({
          totalCount: 0,
          avg_adoption: 0,
          geographies_count: 0,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [
    filters,
    pagination.currentPage,
    pagination.rowsPerPage,
    maturityLevel
  ]);

  /* ----------------------------------------------------------------------------------------------
     LOCAL STORAGE
  ---------------------------------------------------------------------------------------------- */

  useEffect(() => {
    localStorage.setItem('globalDashboardFilters', JSON.stringify(filters));
  }, [filters]);

  useEffect(() => {
    localStorage.setItem('globalDashboardMaturityLevel', maturityLevel);
  }, [maturityLevel]);

  /* ----------------------------------------------------------------------------------------------
     HANDLERS
  ---------------------------------------------------------------------------------------------- */

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
    setPagination((prev) => ({ ...prev, currentPage: 1 }));
  };

  const handlePageChange = (direction) => {
    setPagination((prev) => ({
      ...prev,
      currentPage: prev.currentPage + direction,
    }));
  };

  const handleMaturityLevelChange = (level) => {
    setMaturityLevel(level);
    setFilters({ geografia: 'todos', fecha: 'todos' });
    setPagination({ currentPage: 1, rowsPerPage: 10 });
  };

  /* ----------------------------------------------------------------------------------------------
     TABLA
  ---------------------------------------------------------------------------------------------- */

  const getTableHeaders = () => {
    if (maturityLevel === 'continuous_integration') {
      return [
        'fecha',
        'geografia',
        'service1_name',
        'analisis_review_7dias_pct',
        'historias_fix_version_pct',
        'repos_nomenclatura_pct',
        'aprobacion_pr_pct',
        'tamano_pr_pct',
        'repos_chimera_pct',
        'tiempo_integracion_pct',
        'tiempo_construcciones_pct',
        'construcciones_correctas_pct',
        'tiempo_arreglar_construcciones_pct',
        'calidad_codigo_pct',
        'items_pruebas_xray_pct',
        'adopcion_total_pct',
      ];
    }

    return [
      'fecha',
      'geografia',
      'service1_name',
      'rfo_ok_pct',
      'dep_pct',
      'adopcion_sn2_pct',
      'calidad_features_pct',
      'seguridad_pct',
      'adopcion_total_pct',
    ];
  };

  const tableHeaders = getTableHeaders();

  const formatGeographyName = (name) => {
    if (!name) return '-';
    if (name === 'COMMERCIAL CLIENT SOLUTIONS') return 'COMM CLIENT SOLUTIONS';
    return name;
  };

  const renderTable = () => {
    if (loading)
      return (
        <tr>
          <td colSpan={tableHeaders.length} className="text-center text-primary font-mono p-4">
            Cargando datos...
          </td>
        </tr>
      );

    if (error)
      return (
        <tr>
          <td colSpan={tableHeaders.length} className="text-center text-red-400 font-mono p-4">
            {error}
          </td>
        </tr>
      );

    if (data.length === 0)
      return (
        <tr>
          <td colSpan={tableHeaders.length} className="text-center text-gray-400 font-mono p-4">
            No hay datos para mostrar.
          </td>
        </tr>
      );

    return data.map((row, index) => (
      <tr key={index} className="hover:bg-primary/10">
        {tableHeaders.map((header) => {
          const value = row[header];
          let displayValue = '-';

          if (value !== null && value !== undefined) {
            if (header.endsWith('_pct')) {
              displayValue = `${parseFloat(value).toFixed(2)}%`;
            } else if (header === 'fecha') {
              displayValue = String(value);
            } else if (header === 'geografia') {
              displayValue = formatGeographyName(String(value));
            } else {
              displayValue = String(value);
            }
          }

          return (
            <td key={header} className="px-4 py-4 font-roboto-mono text-sm text-white/70">
              {displayValue}
            </td>
          );
        })}
      </tr>
    ));
  };

  /* ----------------------------------------------------------------------------------------------
     RENDER PRINCIPAL
  ---------------------------------------------------------------------------------------------- */

  return (
    <div className="flex w-full flex-col gap-6">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <h1 className="font-orbitron text-4xl font-bold text-white">
          Nivel de Madurez{' '}
          {maturityLevel === 'practitioner' ? 'Practitioner' : 'CI'}
        </h1>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleMaturityLevelChange('practitioner')}
            className={`px-4 py-2 text-sm font-bold rounded-lg ${
              maturityLevel === 'practitioner'
                ? 'bg-primary text-white shadow-glow-primary'
                : 'bg-primary/20 text-white/70 hover:bg-primary/30'
            }`}
          >
            PRACTITIONER
          </button>

          <button
            onClick={() =>
              handleMaturityLevelChange('continuous_integration')
            }
            className={`px-4 py-2 text-sm font-bold rounded-lg ${
              maturityLevel === 'continuous_integration'
                ? 'bg-primary text-white shadow-glow-primary'
                : 'bg-primary/20 text-white/70 hover:bg-primary/30'
            }`}
          >
            CONTINUOUS INTEGRATION
          </button>
        </div>
      </header>

      {/* KPIs */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="flex flex-col gap-2 rounded-lg bg-primary/5 border border-primary/20 p-6">
          <p className="font-mono text-base text-white/80">
            Total de Registros
          </p>
          <p className="font-orbitron text-3xl font-bold text-white">
            {loading ? '...' : summaryData.totalCount.toLocaleString('es-ES')}
          </p>
        </div>

        <div className="flex flex-col gap-2 rounded-lg bg-primary/5 border border-primary/20 p-6">
          <p className="font-mono text-base text-white/80">
            Geografías Analizadas
          </p>
          <p className="font-orbitron text-3xl font-bold text-white">
            {loading ? '...' : summaryData.geographies_count}
          </p>
        </div>

        <div className="flex flex-col gap-2 rounded-lg bg-primary/5 border border-primary/20 p-6">
          <p className="font-mono text-base text-white/80">
            Adopción Total Promedio
          </p>
          <p className="font-orbitron text-3xl font-bold text-white">
            {loading ? '...' : `${summaryData.avg_adoption.toFixed(2)}%`}
          </p>
        </div>
      </section>

      {/* FILTROS */}
      <section>
        <h2 className="font-orbitron text-2xl font-bold text-white mb-4">
          Filtros
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="text-sm text-primary uppercase tracking-wider">
              Fecha
            </label>

            <select
              id="fecha-filter"
              name="fecha"
              value={filters.fecha}
              onChange={handleFilterChange}
              className="form-select w-full h-12 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg"
            >
              <option value="todos">Todas</option>
              {filterOptions.fechas?.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-primary uppercase tracking-wider">
              Geografía
            </label>

            <select
              id="geografia-filter"
              name="geografia"
              value={filters.geografia}
              onChange={handleFilterChange}
              className="form-select w-full h-12 pl-4 pr-10 bg-black/40 border border-primary/30 text-white rounded-lg"
            >
              <option value="todos">Todas</option>
              {filterOptions.geografias?.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* PIE */}
      <section>
        <h2 className="font-orbitron text-2xl font-bold text-white mb-4">
          Niveles de Certificación por % de Adopción
        </h2>

        <div className="rounded-lg border border-primary/20 bg-primary/5 p-6">
          <PieChart data={certificationLevels} />
        </div>
      </section>

      {/* BARRAS */}
      <section>
        <h2 className="font-orbitron text-2xl font-bold text-white mb-4">
          Niveles de Certificación por Geografía
        </h2>

        <div className="rounded-lg border border-primary/20 bg-primary/5 p-6">
          <StackedBarChart data={geoCertificationData} />
        </div>
      </section>

      {/* TABLA */}
      <section>
        <h2 className="font-orbitron text-2xl font-bold text-white mb-4">
          Cálculo de los KPI's
        </h2>

        <div className="overflow-hidden rounded-lg border border-primary/20 bg-primary/5">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px] table-auto">
              <thead className="bg-primary/20">
                <tr>
                  {tableHeaders.map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 font-mono text-sm text-white/80 uppercase"
                    >
                      {h.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-primary/20">
                {renderTable()}
              </tbody>
            </table>

            {/* PAGINACIÓN */}
            <div className="flex items-center justify-between border-t border-primary/20 px-4 py-3 font-mono">
              <button
                onClick={() => handlePageChange(-1)}
                disabled={pagination.currentPage === 1}
                className="px-4 py-2 bg-black/40 border border-primary/30 text-white/70 rounded-md disabled:opacity-50"
              >
                Anterior
              </button>

              <p className="text-white/70">
                {totalCount > 0
                  ? `Mostrando ${
                      (pagination.currentPage - 1) * pagination.rowsPerPage + 1
                    } a ${Math.min(
                      pagination.currentPage * pagination.rowsPerPage,
                      totalCount
                    )} de ${totalCount}`
                  : '0 resultados'}
              </p>

              <button
                onClick={() => handlePageChange(1)}
                disabled={
                  pagination.currentPage * pagination.rowsPerPage >= totalCount
                }
                className="px-4 py-2 bg-black/40 border border-primary/30 text-white/70 rounded-md disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
