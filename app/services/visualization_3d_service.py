import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sympy as sp
from sympy import lambdify, symbols
import base64
import io
import json
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from scipy.interpolate import griddata
from scipy.spatial import ConvexHull
import warnings

# Suprimir warnings desnecessários
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class Advanced3DVisualizationService:
    """
    Serviço avançado para visualizações 3D de funções matemáticas.
    """
    
    def __init__(self):
        self.x, self.y, self.z = symbols('x y z')
    
    def create_surface_plot(self, 
                          function_str: str, 
                          x_range: Tuple[float, float] = (-5, 5),
                          y_range: Tuple[float, float] = (-5, 5),
                          resolution: int = 50,
                          colorscale: str = 'viridis',
                          title: str = None) -> Dict[str, Any]:
        """
        Cria gráfico 3D de superfície para função de duas variáveis.
        """
        try:
            # Processar função
            expr = sp.sympify(function_str.replace('^', '**'))
            func = lambdify((self.x, self.y), expr, modules=['numpy'])
            
            # Criar grade de pontos
            x_vals = np.linspace(x_range[0], x_range[1], resolution)
            y_vals = np.linspace(y_range[0], y_range[1], resolution)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Calcular valores Z com tratamento de erros
            Z = np.zeros_like(X)
            valid_mask = np.ones_like(X, dtype=bool)
            
            for i in range(resolution):
                for j in range(resolution):
                    try:
                        z_val = func(X[i, j], Y[i, j])
                        if np.isfinite(z_val) and not np.isnan(z_val):
                            Z[i, j] = float(z_val)
                        else:
                            valid_mask[i, j] = False
                    except:
                        valid_mask[i, j] = False
            
            # Aplicar máscara para valores inválidos
            Z[~valid_mask] = np.nan
            
            # Criar gráfico Plotly
            fig = go.Figure(data=[go.Surface(
                x=X, y=Y, z=Z,
                colorscale=colorscale,
                showscale=True,
                hovertemplate='x: %{x}<br>y: %{y}<br>z: %{z}<extra></extra>',
                opacity=0.9
            )])
            
            fig.update_layout(
                title=title or f'Superfície: {function_str}',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    ),
                    aspectmode='cube'
                ),
                width=800,
                height=600,
                font=dict(size=12)
            )
            
            # Converter para JSON
            plotly_json = fig.to_json()
            
            # Estatísticas da superfície
            valid_z = Z[valid_mask]
            stats = {
                'min_z': float(np.min(valid_z)) if len(valid_z) > 0 else None,
                'max_z': float(np.max(valid_z)) if len(valid_z) > 0 else None,
                'mean_z': float(np.mean(valid_z)) if len(valid_z) > 0 else None,
                'valid_points': int(np.sum(valid_mask)),
                'total_points': int(resolution * resolution)
            }
            
            return {
                'success': True,
                'plotly_json': plotly_json,
                'plot_type': 'surface',
                'function': function_str,
                'statistics': stats,
                'interactive': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de superfície: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar superfície 3D: {str(e)}"
            }
    
    def create_contour_3d(self,
                         function_str: str,
                         x_range: Tuple[float, float] = (-5, 5),
                         y_range: Tuple[float, float] = (-5, 5),
                         z_levels: int = 20,
                         resolution: int = 100) -> Dict[str, Any]:
        """
        Cria gráfico de contorno 3D com linhas de nível.
        """
        try:
            # Processar função
            expr = sp.sympify(function_str.replace('^', '**'))
            func = lambdify((self.x, self.y), expr, modules=['numpy'])
            
            # Criar grade de pontos
            x_vals = np.linspace(x_range[0], x_range[1], resolution)
            y_vals = np.linspace(y_range[0], y_range[1], resolution)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Calcular valores Z
            Z = np.zeros_like(X)
            for i in range(resolution):
                for j in range(resolution):
                    try:
                        Z[i, j] = func(X[i, j], Y[i, j])
                    except:
                        Z[i, j] = np.nan
            
            # Criar subplots com contorno 2D e superfície 3D
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{'type': 'surface'}, {'type': 'contour'}]],
                subplot_titles=['Superfície 3D', 'Contornos 2D']
            )
            
            # Adicionar superfície 3D
            fig.add_trace(
                go.Surface(
                    x=X, y=Y, z=Z,
                    colorscale='viridis',
                    showscale=False,
                    opacity=0.8
                ),
                row=1, col=1
            )
            
            # Adicionar contorno 2D
            fig.add_trace(
                go.Contour(
                    x=x_vals, y=y_vals, z=Z,
                    colorscale='viridis',
                    ncontours=z_levels,
                    showscale=True
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title=f'Análise de Contorno: {function_str}',
                height=500,
                width=1000
            )
            
            return {
                'success': True,
                'plotly_json': fig.to_json(),
                'plot_type': 'contour_3d',
                'function': function_str,
                'levels': z_levels
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de contorno: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar contorno 3D: {str(e)}"
            }
    
    def create_vector_field_3d(self,
                              fx_str: str,
                              fy_str: str, 
                              fz_str: str,
                              x_range: Tuple[float, float] = (-3, 3),
                              y_range: Tuple[float, float] = (-3, 3),
                              z_range: Tuple[float, float] = (-3, 3),
                              density: int = 10) -> Dict[str, Any]:
        """
        Cria campo vetorial 3D.
        """
        try:
            # Processar funções vetoriais
            fx_expr = sp.sympify(fx_str.replace('^', '**'))
            fy_expr = sp.sympify(fy_str.replace('^', '**'))
            fz_expr = sp.sympify(fz_str.replace('^', '**'))
            
            fx_func = lambdify((self.x, self.y, self.z), fx_expr, modules=['numpy'])
            fy_func = lambdify((self.x, self.y, self.z), fy_expr, modules=['numpy'])
            fz_func = lambdify((self.x, self.y, self.z), fz_expr, modules=['numpy'])
            
            # Criar grade de pontos
            x_vals = np.linspace(x_range[0], x_range[1], density)
            y_vals = np.linspace(y_range[0], y_range[1], density)
            z_vals = np.linspace(z_range[0], z_range[1], density)
            X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals)
            
            # Calcular componentes do campo vetorial
            U = np.zeros_like(X)
            V = np.zeros_like(Y)
            W = np.zeros_like(Z)
            
            for i in range(density):
                for j in range(density):
                    for k in range(density):
                        try:
                            U[i, j, k] = fx_func(X[i, j, k], Y[i, j, k], Z[i, j, k])
                            V[i, j, k] = fy_func(X[i, j, k], Y[i, j, k], Z[i, j, k])
                            W[i, j, k] = fz_func(X[i, j, k], Y[i, j, k], Z[i, j, k])
                        except:
                            U[i, j, k] = V[i, j, k] = W[i, j, k] = 0
            
            # Achatar arrays para Plotly
            x_flat = X.flatten()
            y_flat = Y.flatten()
            z_flat = Z.flatten()
            u_flat = U.flatten()
            v_flat = V.flatten()
            w_flat = W.flatten()
            
            # Criar gráfico de campo vetorial
            fig = go.Figure(data=go.Cone(
                x=x_flat, y=y_flat, z=z_flat,
                u=u_flat, v=v_flat, w=w_flat,
                colorscale='viridis',
                sizemode="absolute",
                sizeref=0.3,
                showscale=True
            ))
            
            fig.update_layout(
                title=f'Campo Vetorial 3D: ({fx_str}, {fy_str}, {fz_str})',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    aspectmode='cube'
                ),
                width=800,
                height=600
            )
            
            return {
                'success': True,
                'plotly_json': fig.to_json(),
                'plot_type': 'vector_field_3d',
                'functions': [fx_str, fy_str, fz_str]
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar campo vetorial 3D: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar campo vetorial 3D: {str(e)}"
            }
    
    def create_parametric_surface(self,
                                x_func: str,
                                y_func: str,
                                z_func: str,
                                u_range: Tuple[float, float] = (0, 2*np.pi),
                                v_range: Tuple[float, float] = (0, np.pi),
                                resolution: int = 50) -> Dict[str, Any]:
        """
        Cria superfície paramétrica 3D.
        """
        try:
            u, v = symbols('u v')
            
            # Processar funções paramétricas
            x_expr = sp.sympify(x_func.replace('^', '**'))
            y_expr = sp.sympify(y_func.replace('^', '**'))
            z_expr = sp.sympify(z_func.replace('^', '**'))
            
            x_func_lambda = lambdify((u, v), x_expr, modules=['numpy'])
            y_func_lambda = lambdify((u, v), y_expr, modules=['numpy'])
            z_func_lambda = lambdify((u, v), z_expr, modules=['numpy'])
            
            # Criar grade paramétrica
            u_vals = np.linspace(u_range[0], u_range[1], resolution)
            v_vals = np.linspace(v_range[0], v_range[1], resolution)
            U, V = np.meshgrid(u_vals, v_vals)
            
            # Calcular coordenadas
            X = np.zeros_like(U)
            Y = np.zeros_like(U)
            Z = np.zeros_like(U)
            
            for i in range(resolution):
                for j in range(resolution):
                    try:
                        X[i, j] = x_func_lambda(U[i, j], V[i, j])
                        Y[i, j] = y_func_lambda(U[i, j], V[i, j])
                        Z[i, j] = z_func_lambda(U[i, j], V[i, j])
                    except:
                        X[i, j] = Y[i, j] = Z[i, j] = np.nan
            
            # Criar gráfico
            fig = go.Figure(data=[go.Surface(
                x=X, y=Y, z=Z,
                colorscale='plasma',
                showscale=True,
                opacity=0.9
            )])
            
            fig.update_layout(
                title=f'Superfície Paramétrica<br>x={x_func}, y={y_func}, z={z_func}',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    aspectmode='cube'
                ),
                width=800,
                height=600
            )
            
            return {
                'success': True,
                'plotly_json': fig.to_json(),
                'plot_type': 'parametric_surface',
                'functions': [x_func, y_func, z_func],
                'parameters': ['u', 'v']
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar superfície paramétrica: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar superfície paramétrica: {str(e)}"
            }
    
    def create_integration_volume_3d(self,
                                   function_str: str,
                                   x_range: Tuple[float, float],
                                   y_range: Tuple[float, float],
                                   show_volume: bool = True,
                                   resolution: int = 30) -> Dict[str, Any]:
        """
        Visualiza volume sob uma superfície (integral dupla).
        """
        try:
            # Processar função
            expr = sp.sympify(function_str.replace('^', '**'))
            func = lambdify((self.x, self.y), expr, modules=['numpy'])
            
            # Criar grade de pontos
            x_vals = np.linspace(x_range[0], x_range[1], resolution)
            y_vals = np.linspace(y_range[0], y_range[1], resolution)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Calcular valores Z
            Z = np.zeros_like(X)
            for i in range(resolution):
                for j in range(resolution):
                    try:
                        z_val = func(X[i, j], Y[i, j])
                        Z[i, j] = max(0, float(z_val))  # Apenas valores positivos para volume
                    except:
                        Z[i, j] = 0
            
            fig = go.Figure()
            
            # Adicionar superfície
            fig.add_trace(go.Surface(
                x=X, y=Y, z=Z,
                colorscale='Blues',
                opacity=0.7,
                name='f(x,y)',
                showscale=True
            ))
            
            if show_volume:
                # Criar "paredes" do volume
                # Parede frontal (y mínimo)
                y_min = np.full_like(X[0, :], y_range[0])
                x_front = X[0, :]
                z_front_top = Z[0, :]
                z_front_bottom = np.zeros_like(z_front_top)
                
                # Criar mesh para parede frontal
                for i in range(len(x_front)-1):
                    x_wall = [x_front[i], x_front[i+1], x_front[i+1], x_front[i]]
                    y_wall = [y_min[i], y_min[i+1], y_min[i+1], y_min[i]]
                    z_wall = [z_front_bottom[i], z_front_bottom[i+1], z_front_top[i+1], z_front_top[i]]
                    
                    fig.add_trace(go.Mesh3d(
                        x=x_wall, y=y_wall, z=z_wall,
                        color='lightblue',
                        opacity=0.3,
                        showscale=False
                    ))
            
            # Calcular volume aproximado
            dx = (x_range[1] - x_range[0]) / resolution
            dy = (y_range[1] - y_range[0]) / resolution
            volume = np.sum(Z) * dx * dy
            
            fig.update_layout(
                title=f'Volume sob f(x,y) = {function_str}<br>Volume ≈ {volume:.4f}',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z',
                    aspectmode='cube'
                ),
                width=800,
                height=600
            )
            
            return {
                'success': True,
                'plotly_json': fig.to_json(),
                'plot_type': 'integration_volume',
                'function': function_str,
                'volume_approximation': float(volume),
                'integration_bounds': {
                    'x_range': x_range,
                    'y_range': y_range
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar visualização de volume: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar volume de integração: {str(e)}"
            }
    
    def create_gradient_field(self,
                            function_str: str,
                            x_range: Tuple[float, float] = (-3, 3),
                            y_range: Tuple[float, float] = (-3, 3),
                            density: int = 15) -> Dict[str, Any]:
        """
        Visualiza campo gradiente de uma função.
        """
        try:
            # Processar função e calcular gradiente
            expr = sp.sympify(function_str.replace('^', '**'))
            grad_x = sp.diff(expr, self.x)
            grad_y = sp.diff(expr, self.y)
            
            func = lambdify((self.x, self.y), expr, modules=['numpy'])
            grad_x_func = lambdify((self.x, self.y), grad_x, modules=['numpy'])
            grad_y_func = lambdify((self.x, self.y), grad_y, modules=['numpy'])
            
            # Criar grade de pontos
            x_vals = np.linspace(x_range[0], x_range[1], density)
            y_vals = np.linspace(y_range[0], y_range[1], density)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Calcular valores da função e gradiente
            Z = np.zeros_like(X)
            U = np.zeros_like(X)  # Componente x do gradiente
            V = np.zeros_like(X)  # Componente y do gradiente
            
            for i in range(density):
                for j in range(density):
                    try:
                        Z[i, j] = func(X[i, j], Y[i, j])
                        U[i, j] = grad_x_func(X[i, j], Y[i, j])
                        V[i, j] = grad_y_func(X[i, j], Y[i, j])
                    except:
                        Z[i, j] = U[i, j] = V[i, j] = 0
            
            # Criar subplots
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{'type': 'surface'}, {'type': 'scatter'}]],
                subplot_titles=['Função 3D', 'Campo Gradiente 2D']
            )
            
            # Adicionar superfície 3D
            fig.add_trace(
                go.Surface(
                    x=X, y=Y, z=Z,
                    colorscale='viridis',
                    showscale=False,
                    opacity=0.8
                ),
                row=1, col=1
            )
            
            # Adicionar campo vetorial 2D (gradiente)
            for i in range(0, density, 2):
                for j in range(0, density, 2):
                    if np.isfinite(U[i, j]) and np.isfinite(V[i, j]):
                        fig.add_trace(
                            go.Scatter(
                                x=[X[i, j], X[i, j] + U[i, j] * 0.2],
                                y=[Y[i, j], Y[i, j] + V[i, j] * 0.2],
                                mode='lines',
                                line=dict(color='red', width=2),
                                showlegend=False
                            ),
                            row=1, col=2
                        )
            
            fig.update_layout(
                title=f'Campo Gradiente: ∇({function_str})',
                height=500,
                width=1000
            )
            
            return {
                'success': True,
                'plotly_json': fig.to_json(),
                'plot_type': 'gradient_field',
                'function': function_str,
                'gradient': [str(grad_x), str(grad_y)]
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar campo gradiente: {str(e)}")
            return {
                'success': False,
                'error': f"Erro ao gerar campo gradiente: {str(e)}"
            }

# Instância global do serviço
visualization_3d_service = Advanced3DVisualizationService() 