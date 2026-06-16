'use client';

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  HiMagnifyingGlass,
  HiMiniBolt,
  HiChevronLeft,
  HiChevronRight,
  HiArrowLeft,
  HiXMark,
  HiFunnel,
  HiChevronUpDown,
  HiChevronUp,
  HiChevronDown,
} from 'react-icons/hi2';
import { BsCarFront, BsFuelPump } from 'react-icons/bs';
import { RiRobot2Fill } from 'react-icons/ri';
import api from '@/lib/api';
import Navbar from '@/components/Navbar';
import styles from './Spesifikasi.module.css';

interface CarKatalog {
  BRAND: string;
  MODEL: string;
  VARIAN: string;
  'BODY TYPE': string;
  HARGAOTR: number;
  'HORSE POWER (HP)': number;
  CC: number;
  FUEL: string;
  TRANSMISSION: string;
  SEAT: number;
  DRIVE_SYS: string;
  WHOLESALES_VARIAN: number;
  RETAIL_BRAND: number;
}

type SortKey = 'BRAND' | 'HARGAOTR' | 'HORSE POWER (HP)' | 'WHOLESALES_VARIAN' | 'RETAIL_BRAND';
type SortDir = 'asc' | 'desc';

const ITEMS_PER_PAGE = 25;

const BODY_TYPES = ['Semua', 'SUV', 'MPV', 'Sedan', 'Hatchback', 'Pickup', 'Van'];

export default function SpesifikasiPage() {
  const [data, setData] = useState<CarKatalog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [bodyFilter, setBodyFilter] = useState('Semua');
  const [page, setPage] = useState(1);
  const [sortKey, setSortKey] = useState<SortKey | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/katalog');
        setData(response.data);
      } catch (err: any) {
        console.error('Gagal mengambil data katalog:', err);
        setError('Gagal memuat data. Pastikan backend server sudah berjalan.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Filter + sort
  const processed = useMemo(() => {
    let result = [...data];

    // Search
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (c) =>
          c.BRAND?.toLowerCase().includes(q) ||
          c.MODEL?.toLowerCase().includes(q) ||
          c.VARIAN?.toLowerCase().includes(q)
      );
    }

    // Body type filter
    if (bodyFilter !== 'Semua') {
      result = result.filter(
        (c) => c['BODY TYPE']?.toLowerCase() === bodyFilter.toLowerCase()
      );
    }

    // Sort
    if (sortKey) {
      result.sort((a, b) => {
        const va = (a as any)[sortKey] ?? 0;
        const vb = (b as any)[sortKey] ?? 0;
        if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
        return sortDir === 'asc' ? va - vb : vb - va;
      });
    }

    return result;
  }, [data, search, bodyFilter, sortKey, sortDir]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(processed.length / ITEMS_PER_PAGE));
  const paginated = processed.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  // Reset page on filter change
  useEffect(() => { setPage(1); }, [search, bodyFilter, sortKey, sortDir]);

  const formatPrice = (price: number | null) => {
    if (!price) return '-';
    if (price >= 1_000_000_000) return `Rp ${(price / 1_000_000_000).toFixed(1)} M`;
    return `Rp ${(price / 1_000_000).toLocaleString('id-ID')} Jt`;
  };

  const formatNumber = (n: number | null) => {
    if (!n) return '0';
    return n.toLocaleString('id-ID');
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col) return <HiChevronUpDown size={14} className={styles.sortIconIdle} />;
    return sortDir === 'asc' ? <HiChevronUp size={14} className={styles.sortIconActive} /> : <HiChevronDown size={14} className={styles.sortIconActive} />;
  };

  return (
    <>
      <Navbar />
      <div className={styles.pageWrap}>
        {/* ── Hero Header ── */}
        <header className={styles.hero}>
          <div className={styles.heroInner}>
            <a href="/" className={styles.backBtn}>
              <HiArrowLeft size={18} />
              <span>Kembali ke Chat</span>
            </a>
            <div className={styles.heroContent}>
              <div className={styles.heroIcon}>
                <BsCarFront size={28} />
              </div>
              <div>
                <h1 className={styles.heroTitle}>Katalog Spesifikasi Mobil</h1>
                <p className={styles.heroSub}>
                  Database lengkap {data.length > 0 ? `${data.length} varian` : ''} mobil — spesifikasi teknis, harga OTR, dan data popularitas pasar Indonesia 2025.
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* ── Controls ── */}
        <div className={styles.controls}>
          <div className={styles.searchBox}>
            <HiMagnifyingGlass className={styles.searchIcon} size={17} />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Cari brand, model, atau varian..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button className={styles.clearBtn} onClick={() => setSearch('')}>
                <HiXMark size={15} />
              </button>
            )}
          </div>

          <div className={styles.filterGroup}>
            <HiFunnel size={14} className={styles.filterIcon} />
            {BODY_TYPES.map((bt) => (
              <button
                key={bt}
                className={`${styles.filterChip} ${bodyFilter === bt ? styles.filterChipActive : ''}`}
                onClick={() => setBodyFilter(bt)}
              >
                {bt}
              </button>
            ))}
          </div>

          <div className={styles.resultCount}>
            <span className={styles.resultNum}>{processed.length}</span> mobil ditemukan
          </div>
        </div>

        {/* ── Table ── */}
        <div className={styles.tableCard}>
          {loading ? (
            <div className={styles.loadingState}>
              <div className={styles.spinner} />
              <span>Memuat data katalog...</span>
            </div>
          ) : error ? (
            <div className={styles.errorState}>
              <p>{error}</p>
              <button className={styles.retryBtn} onClick={() => window.location.reload()}>
                Coba Lagi
              </button>
            </div>
          ) : (
            <>
              <div className={styles.tableScroll}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th className={styles.thSticky}>#</th>
                      <th className={styles.thSticky}>
                        <button className={styles.sortBtn} onClick={() => handleSort('BRAND')}>
                          Mobil <SortIcon col="BRAND" />
                        </button>
                      </th>
                      <th>Tipe</th>
                      <th>
                        <button className={styles.sortBtn} onClick={() => handleSort('HARGAOTR')}>
                          Harga OTR <SortIcon col="HARGAOTR" />
                        </button>
                      </th>
                      <th>
                        <button className={styles.sortBtn} onClick={() => handleSort('HORSE POWER (HP)')}>
                          Mesin <SortIcon col="HORSE POWER (HP)" />
                        </button>
                      </th>
                      <th>Drivetrain</th>
                      <th>
                        <button className={styles.sortBtn} onClick={() => handleSort('WHOLESALES_VARIAN')}>
                          Wholesales <SortIcon col="WHOLESALES_VARIAN" />
                        </button>
                      </th>
                      <th>
                        <button className={styles.sortBtn} onClick={() => handleSort('RETAIL_BRAND')}>
                          Retail Brand <SortIcon col="RETAIL_BRAND" />
                        </button>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginated.map((car, idx) => (
                      <tr key={idx} className={styles.row}>
                        <td className={styles.rowNum}>{(page - 1) * ITEMS_PER_PAGE + idx + 1}</td>
                        <td className={styles.carCell}>
                          <span className={styles.brandTag}>{car.BRAND}</span>
                          <div className={styles.carName}>{car.MODEL}</div>
                          <div className={styles.carVarian}>{car.VARIAN}</div>
                        </td>
                        <td>
                          <span className={styles.bodyTag}>{car['BODY TYPE'] || '-'}</span>
                        </td>
                        <td className={styles.priceCell}>{formatPrice(car.HARGAOTR)}</td>
                        <td>
                          <div className={styles.specStack}>
                            <span className={styles.specChip}>
                              <HiMiniBolt size={12} />
                              {car['HORSE POWER (HP)'] || '-'} HP
                            </span>
                            <span className={styles.specChip}>
                              <BsFuelPump size={11} />
                              {car.CC ? `${car.CC} cc` : 'EV'} · {car.FUEL || '-'}
                            </span>
                          </div>
                        </td>
                        <td>
                          <div className={styles.specStack}>
                            <span className={styles.driveTag}>{car.DRIVE_SYS || '-'}</span>
                            <span className={styles.seatInfo}>{car.SEAT || '-'} Seat · {car.TRANSMISSION || '-'}</span>
                          </div>
                        </td>
                        <td>
                          <div className={styles.salesCell}>
                            <span className={styles.salesNum}>{formatNumber(car.WHOLESALES_VARIAN)}</span>
                            <span className={styles.salesLabel}>unit</span>
                          </div>
                        </td>
                        <td>
                          <div className={styles.salesCell}>
                            <span className={styles.salesNumRetail}>{formatNumber(car.RETAIL_BRAND)}</span>
                            <span className={styles.salesLabel}>unit</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {paginated.length === 0 && (
                      <tr>
                        <td colSpan={8} className={styles.emptyRow}>
                          <BsCarFront size={32} />
                          <p>Tidak ada mobil yang cocok dengan filter Anda</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* ── Pagination ── */}
              {totalPages > 1 && (
                <div className={styles.pagination}>
                  <button
                    className={styles.pageBtn}
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    <HiChevronLeft size={16} />
                  </button>
                  <div className={styles.pageInfo}>
                    Halaman <span className={styles.pageCurrent}>{page}</span> dari{' '}
                    <span>{totalPages}</span>
                  </div>
                  <button
                    className={styles.pageBtn}
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    <HiChevronRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
