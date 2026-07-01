import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import type { IChartApi, ISeriesApi, CandlestickData } from 'lightweight-charts';

interface ChartProps {
  data: CandlestickData[];
  width?: number;
  height?: number;
  symbol: string;
}

export const CandlestickChart: React.FC<ChartProps> = ({ data, width, height = 400, symbol }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1, // Normal mode
        vertLine: { color: '#2979ff', style: 3, width: 1, labelBackgroundColor: '#2979ff' },
        horzLine: { color: '#2979ff', style: 3, width: 1, labelBackgroundColor: '#2979ff' },
      }
    });

    chartRef.current = chart;

    // Add candlestick series (v5 API)
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#00e676',
      downColor: '#ff5252',
      borderVisible: false,
      wickUpColor: '#00e676',
      wickDownColor: '#ff5252',
    });

    candlestickSeries.setData(data);
    seriesRef.current = candlestickSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, height]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div 
        style={{ 
          position: 'absolute', 
          top: 12, 
          left: 12, 
          zIndex: 10, 
          color: 'var(--text-primary)', 
          fontWeight: 700,
          fontSize: '1.2rem',
          textShadow: '0px 1px 3px rgba(0,0,0,0.8)'
        }}
      >
        {symbol}
      </div>
      <div ref={chartContainerRef} style={{ width: '100%', height: height }} />
    </div>
  );
};
