"""
OCRScanner - Escaneo y OCR en tiempo real
Para el feature "Deep Fusion Scanning".
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from loguru import logger

# Lazy imports
paddleocr = None
pytesseract = None


def _ensure_paddleocr():
    """Carga PaddleOCR de forma lazy."""
    global paddleocr
    if paddleocr is None:
        try:
            from paddleocr import PaddleOCR
            paddleocr = PaddleOCR(use_angle_cls=True, lang='es', show_log=False)
            logger.info("PaddleOCR cargado.")
        except ImportError:
            logger.warning("PaddleOCR no disponible. Usando Tesseract como fallback.")
            _ensure_tesseract()


def _ensure_tesseract():
    """Carga Tesseract de forma lazy."""
    global pytesseract
    if pytesseract is None:
        try:
            import pytesseract as _pt
            pytesseract = _pt
            logger.info("Tesseract cargado.")
        except ImportError:
            logger.error("Ni PaddleOCR ni Tesseract están instalados.")
            raise


@dataclass
class DetectedDocument:
    """Documento detectado en el frame."""
    corners: np.ndarray  # 4 esquinas
    warped_image: np.ndarray  # Imagen corregida
    text: str = ""
    confidence: float = 0.0


class OCRScanner:
    """
    Escáner de documentos con detección y OCR en tiempo real.
    Detecta documentos/pantallas y extrae texto.
    """
    
    def __init__(self, use_paddle: bool = True):
        self._use_paddle = use_paddle
        self._last_document: Optional[DetectedDocument] = None
        self._min_area = 10000  # Área mínima para detectar documento
    
    def detect_document(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta un documento rectangular en el frame.
        
        Returns:
            Corners del documento (4 puntos) o None
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Blur y detección de bordes
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilatar para conectar bordes
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Buscar el contorno más grande que sea un cuadrilátero
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            area = cv2.contourArea(contour)
            if area < self._min_area:
                continue
            
            # Aproximar polígono
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4:
                return approx.reshape(4, 2)
        
        return None
    
    def warp_document(self, frame: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """
        Aplica transformación de perspectiva para corregir el documento.
        """
        # Ordenar puntos: top-left, top-right, bottom-right, bottom-left
        rect = self._order_points(corners)
        (tl, tr, br, bl) = rect
        
        # Calcular dimensiones del documento corregido
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_width = max(int(width_a), int(width_b))
        
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_height = max(int(height_a), int(height_b))
        
        # Destino
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ], dtype="float32")
        
        # Transformación
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(frame, M, (max_width, max_height))
        
        return warped
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Ordena puntos en sentido horario desde top-left."""
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left
        
        return rect
    
    def extract_text(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extrae texto de una imagen usando OCR.
        
        Returns:
            Tuple[str, float]: (texto extraído, confianza promedio)
        """
        if self._use_paddle:
            return self._extract_with_paddle(image)
        else:
            return self._extract_with_tesseract(image)
    
    def _extract_with_paddle(self, image: np.ndarray) -> Tuple[str, float]:
        """Extrae texto usando PaddleOCR."""
        _ensure_paddleocr()
        
        try:
            result = paddleocr.ocr(image, cls=True)
            
            if not result or not result[0]:
                return "", 0.0
            
            texts = []
            confidences = []
            
            for line in result[0]:
                text = line[1][0]
                conf = line[1][1]
                texts.append(text)
                confidences.append(conf)
            
            full_text = "\n".join(texts)
            avg_conf = np.mean(confidences) if confidences else 0.0
            
            return full_text, float(avg_conf)
            
        except Exception as e:
            logger.error(f"Error en PaddleOCR: {e}")
            return "", 0.0
    
    def _extract_with_tesseract(self, image: np.ndarray) -> Tuple[str, float]:
        """Extrae texto usando Tesseract."""
        _ensure_tesseract()
        
        try:
            # Preprocesar para mejor OCR
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            text = pytesseract.image_to_string(gray, lang='spa')
            
            # Tesseract no da confianza fácilmente, estimamos
            confidence = 0.7 if len(text.strip()) > 10 else 0.3
            
            return text.strip(), confidence
            
        except Exception as e:
            logger.error(f"Error en Tesseract: {e}")
            return "", 0.0
    
    def scan(self, frame: np.ndarray) -> Optional[DetectedDocument]:
        """
        Pipeline completo: detectar documento, corregir perspectiva, extraer texto.
        """
        corners = self.detect_document(frame)
        
        if corners is None:
            return None
        
        warped = self.warp_document(frame, corners)
        text, confidence = self.extract_text(warped)
        
        doc = DetectedDocument(
            corners=corners,
            warped_image=warped,
            text=text,
            confidence=confidence
        )
        
        self._last_document = doc
        return doc
    
    def draw_detection(self, frame: np.ndarray, doc: DetectedDocument):
        """Dibuja la detección en el frame."""
        # Dibujar contorno del documento
        pts = doc.corners.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
        
        # Etiqueta
        cv2.putText(
            frame, f"Doc detectado ({doc.confidence:.0%})",
            (int(doc.corners[0][0]), int(doc.corners[0][1]) - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
        )
