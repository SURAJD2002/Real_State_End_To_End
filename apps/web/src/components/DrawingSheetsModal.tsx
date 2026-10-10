import React, { useState, useEffect } from 'react';
import {
  Download,
  Code,
  X,
  Compass,
  AlertTriangle,
  FileCode
} from 'lucide-react';

interface DrawingSheet {
  drawingId: string;
  drawingTitle: string;
  viewType: string;
  sheetNumber: string;
  scale: string;
  sheetSize: string;
  description: string;
  svgUrl: string;
  pdfUrl: string;
  metadataUrl: string;
}

interface DrawingSetResponse {
  designVersionId: string;
  modelHash: string;
  totalSheets: number;
  compilerVersion: string;
  status: string;
  drawings: DrawingSheet[];
}

interface DrawingSheetsModalProps {
  isOpen: boolean;
  onClose: () => void;
  designVersionId: string;
  optionLabel?: string;
}

export const DrawingSheetsModal: React.FC<DrawingSheetsModalProps> = ({
  isOpen,
  onClose,
  designVersionId,
  optionLabel = 'Option B — Family 3BHK'
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [drawingSet, setDrawingSet] = useState<DrawingSetResponse | null>(null);
  const [selectedDrawing, setSelectedDrawing] = useState<DrawingSheet | null>(null);
  const [previewSvg, setPreviewSvg] = useState<string | null>(null);
  const [loadingSvg, setLoadingSvg] = useState<boolean>(false);
  const [isTechnicalMode, setIsTechnicalMode] = useState<boolean>(false);
  const [technicalTab, setTechnicalTab] = useState<'MANIFEST' | 'CBM_IDS' | 'COMPILER'>('MANIFEST');
  const [activeMetadata, setActiveMetadata] = useState<any>(null);

  // Fetch drawings list
  useEffect(() => {
    if (!isOpen || !designVersionId) return;

    setLoading(true);
    setError(null);
    fetch(`/api/v1/design-versions/${encodeURIComponent(designVersionId)}/drawings`)
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`Failed to load drawings: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data: DrawingSetResponse) => {
        setDrawingSet(data);
        if (data.drawings && data.drawings.length > 0) {
          setSelectedDrawing(data.drawings[0]);
        }
      })
      .catch((err) => {
        console.error('Error fetching drawings:', err);
        setError(err.message || 'Failed to load drawing set');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [isOpen, designVersionId]);

  // Fetch SVG preview when selected drawing changes
  useEffect(() => {
    if (!selectedDrawing) return;

    setLoadingSvg(true);
    fetch(selectedDrawing.svgUrl)
      .then(async (res) => {
        if (!res.ok) throw new Error('Failed to load SVG preview');
        return res.text();
      })
      .then((svgText) => {
        setPreviewSvg(svgText);
      })
      .catch((err) => {
        console.error('Error loading SVG preview:', err);
        setPreviewSvg(null);
      })
      .finally(() => {
        setLoadingSvg(false);
      });

    // Also fetch detailed drawing metadata for technical view
    fetch(selectedDrawing.metadataUrl)
      .then(res => res.ok ? res.json() : null)
      .then(meta => setActiveMetadata(meta))
      .catch(() => setActiveMetadata(null));
  }, [selectedDrawing]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-7xl h-[92vh] flex flex-col rounded-2xl bg-slate-950 border border-slate-800 shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-display font-bold text-lg text-white">
                  Architectural Drawing Set
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  ISO 128 / A3 LANDSCAPE
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {optionLabel} • <span className="font-mono text-slate-300">{designVersionId}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Technical Mode Toggle */}
            <button
              onClick={() => setIsTechnicalMode(!isTechnicalMode)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center gap-1.5 ${
                isTechnicalMode
                  ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                  : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" />
              <span>{isTechnicalMode ? 'Technical Mode' : 'Customer View'}</span>
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* Left Column: Drawing Sheet Navigation */}
          <div className="w-full md:w-80 border-r border-slate-800 bg-slate-900/30 flex flex-col overflow-y-auto">
            <div className="p-4 border-b border-slate-800/60 bg-slate-900/50 flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
                Drawing Sheets ({drawingSet?.totalSheets || 0})
              </span>
              <span className="text-[10px] font-mono text-slate-400">1:100 METRIC</span>
            </div>

            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                Loading architectural drawings...
              </div>
            ) : error ? (
              <div className="p-4 m-3 rounded-lg bg-red-950/40 border border-red-800/50 text-red-300 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
                <span>{error}</span>
              </div>
            ) : (
              <div className="p-2 space-y-1">
                {drawingSet?.drawings.map((dwg) => {
                  const isSelected = selectedDrawing?.drawingId === dwg.drawingId;
                  return (
                    <button
                      key={dwg.drawingId}
                      onClick={() => setSelectedDrawing(dwg)}
                      className={`w-full text-left p-3 rounded-xl transition-all flex items-start justify-between gap-2 border ${
                        isSelected
                          ? 'bg-blue-600/15 border-blue-500/50 text-white shadow-sm'
                          : 'bg-transparent border-transparent text-slate-300 hover:bg-slate-800/50 hover:text-white'
                      }`}
                    >
                      <div>
                        {isTechnicalMode ? (
                          <div className="flex items-center gap-1.5">
                            <span className="text-[11px] font-mono font-bold text-blue-400">
                              {dwg.drawingId}
                            </span>
                            <span className="text-[10px] font-mono text-slate-400">
                              [{dwg.sheetNumber}]
                            </span>
                          </div>
                        ) : null}
                        <div className="text-xs font-semibold mt-0.5 leading-snug">
                          {dwg.drawingTitle}
                        </div>
                      </div>
                      {isTechnicalMode && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/50 shrink-0">
                          {dwg.scale}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Legal Notice */}
            <div className="mt-auto p-4 border-t border-slate-800/80 bg-slate-950/80">
              <div className="text-[10px] text-slate-400 leading-relaxed">
                <span className="font-semibold text-slate-300 block mb-0.5">Professional Review Status:</span>
                Drawings are computed directly from the Canonical Building Model. Subject to review and certification by a licensed architect or engineer.
              </div>
            </div>
          </div>

          {/* Right Area: Preview & Actions */}
          <div className="flex-1 flex flex-col bg-slate-950 overflow-hidden">
            {/* Top Toolbar for Active Sheet */}
            {selectedDrawing && (
              <div className="px-6 py-3 border-b border-slate-800 bg-slate-900/40 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h4 className="font-display font-bold text-sm text-white flex items-center gap-2">
                    <span>{selectedDrawing.drawingId}: {selectedDrawing.drawingTitle}</span>
                  </h4>
                  <p className="text-xs text-slate-400">
                    {selectedDrawing.description}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <a
                    href={selectedDrawing.pdfUrl}
                    target="_blank"
                    rel="noreferrer"
                    download
                    className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF (A3)</span>
                  </a>

                  <a
                    href={selectedDrawing.svgUrl}
                    target="_blank"
                    rel="noreferrer"
                    download
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors flex items-center gap-1.5"
                  >
                    <FileCode className="w-3.5 h-3.5" />
                    <span>Download SVG</span>
                  </a>
                </div>
              </div>
            )}

            {/* Technical View vs Customer Vector Viewport */}
            {isTechnicalMode ? (
              <div className="flex-1 flex flex-col p-6 overflow-y-auto bg-slate-950">
                <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
                  <button
                    onClick={() => setTechnicalTab('MANIFEST')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                      technicalTab === 'MANIFEST'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Drawing Manifest
                  </button>
                  <button
                    onClick={() => setTechnicalTab('CBM_IDS')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                      technicalTab === 'CBM_IDS'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Source CBM IDs ({activeMetadata?.sourceElementCount || 0})
                  </button>
                  <button
                    onClick={() => setTechnicalTab('COMPILER')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors ${
                      technicalTab === 'COMPILER'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-900 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    Compiler Details
                  </button>
                </div>

                {technicalTab === 'MANIFEST' && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs">
                      <div className="text-slate-400 mb-1">// Canonical Release &amp; Compiler Integrity</div>
                      <div className="text-emerald-400">Design Version: {designVersionId}</div>
                      <div className="text-slate-300">Model Hash: {drawingSet?.modelHash}</div>
                      <div className="text-slate-300">Compiler Engine: Planwise Drawing Compiler v{drawingSet?.compilerVersion}</div>
                      <div className="text-slate-300">Deterministic Timestamp: 2026-10-02T12:00:00Z</div>
                      <div className="text-blue-400 mt-2">Active Drawing: {selectedDrawing?.drawingId} ({selectedDrawing?.drawingTitle})</div>
                    </div>
                  </div>
                )}

                {technicalTab === 'CBM_IDS' && (
                  <div className="space-y-3">
                    <p className="text-xs text-slate-400">
                      Authoritative CBM elements projected directly into this sheet:
                    </p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-xs">
                      {(activeMetadata?.sourceElementIds || []).map((id: string, i: number) => (
                        <div key={i} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 flex items-center justify-between">
                          <span>{id}</span>
                          <span className="text-[10px] text-blue-400">CBM</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {technicalTab === 'COMPILER' && (
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 space-y-2">
                    <div className="font-semibold text-white">ISO 128 Drawing Standards Implementation:</div>
                    <ul className="list-disc list-inside space-y-1 text-slate-400">
                      <li>Sheet Size: A3 Landscape (420 × 297 mm / 1190.55 × 841.89 pt)</li>
                      <li>Architectural Scale: 1:100 (1 meter = 28.3465 pt on paper)</li>
                      <li>Line Weights: Heavy cut wall 0.50 mm (1.42 pt), visible 0.35 mm (0.99 pt), dimension 0.13 mm (0.35 pt)</li>
                      <li>True North: SECS UTM Azimuth 0.0° (+Y coordinate axis)</li>
                      <li>Title Block: Standard ISO 7200 / Planwise Enterprise title block in sheet corner</li>
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              /* Vector SVG Viewport Preview */
              <div className="flex-1 bg-slate-900/60 p-4 flex items-center justify-center overflow-auto">
                {loadingSvg ? (
                  <div className="text-center text-xs text-slate-400">
                    <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    Rendering publication drawing vector sheet...
                  </div>
                ) : previewSvg ? (
                  <div
                    className="w-full h-full max-h-[75vh] flex items-center justify-center rounded-xl bg-white shadow-xl overflow-hidden p-2"
                    dangerouslySetInnerHTML={{ __html: previewSvg }}
                  />
                ) : (
                  <div className="text-center text-xs text-slate-400">
                    No preview available for this drawing.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
