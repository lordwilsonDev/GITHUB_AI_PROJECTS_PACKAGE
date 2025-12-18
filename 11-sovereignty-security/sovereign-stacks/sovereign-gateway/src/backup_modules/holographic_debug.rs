// HOLOGRAPHIC DEBUGGING MODULE
// 3D visualization of request flows and system state

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// 3D coordinate in holographic space
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Vector3D {
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

/// Holographic node representing a system component
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolographicNode {
    pub id: String,
    pub position: Vector3D,
    pub node_type: NodeType,
    pub size: f32,
    pub color: Color,
    pub activity_level: f32,
    pub connections: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum NodeType {
    Gateway,
    Tool,
    Container,
    FileSystem,
    Network,
    Process,
    Cache,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Color {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: f32,
}

/// Request flow visualization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequestFlow {
    pub flow_id: String,
    pub path: Vec<FlowPoint>,
    pub duration_ms: u64,
    pub torsion_map: Vec<f32>,
    pub status: FlowStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowPoint {
    pub node_id: String,
    pub timestamp: u64,
    pub position: Vector3D,
    pub velocity: Vector3D,
    pub torsion: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FlowStatus {
    Active,
    Completed,
    Failed,
    Blocked,
}

/// Holographic scene containing all visualizations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HolographicScene {
    pub nodes: HashMap<String, HolographicNode>,
    pub flows: Vec<RequestFlow>,
    pub camera: Camera,
    pub timestamp: u64,
    pub metrics_overlay: MetricsOverlay,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Camera {
    pub position: Vector3D,
    pub target: Vector3D,
    pub fov: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricsOverlay {
    pub total_requests: u64,
    pub active_flows: usize,
    pub avg_torsion: f32,
    pub system_health: f32,
    pub hotspots: Vec<String>,
}

/// Holographic Debugger
pub struct HolographicDebugger {
    scene: HolographicScene,
    layout_algorithm: LayoutAlgorithm,
    animation_speed: f32,
}

#[derive(Debug, Clone, PartialEq)]
pub enum LayoutAlgorithm {
    ForceDirected,
    Hierarchical,
    Circular,
    Grid,
}

impl HolographicDebugger {
    pub fn new() -> Self {
        Self {
            scene: HolographicScene {
                nodes: HashMap::new(),
                flows: Vec::new(),
                camera: Camera {
                    position: Vector3D { x: 0.0, y: 5.0, z: 10.0 },
                    target: Vector3D { x: 0.0, y: 0.0, z: 0.0 },
                    fov: 60.0,
                },
                timestamp: 0,
                metrics_overlay: MetricsOverlay {
                    total_requests: 0,
                    active_flows: 0,
                    avg_torsion: 0.0,
                    system_health: 1.0,
                    hotspots: Vec::new(),
                },
            },
            layout_algorithm: LayoutAlgorithm::ForceDirected,
            animation_speed: 1.0,
        }
    }

    /// Add a node to the holographic scene
    pub fn add_node(&mut self, node: HolographicNode) {
        self.scene.nodes.insert(node.id.clone(), node);
        self.recalculate_layout();
    }

    /// Record a request flow
    pub fn record_flow(&mut self, flow: RequestFlow) {
        self.scene.flows.push(flow);
        self.update_metrics();
    }

    /// Get current scene state
    pub fn get_scene(&self) -> &HolographicScene {
        &self.scene
    }

    /// Generate ASCII art visualization (for terminal display)
    pub fn render_ascii(&self, width: usize, height: usize) -> String {
        let mut canvas = vec![vec![' '; width]; height];
        
        // Project 3D nodes to 2D canvas
        for node in self.scene.nodes.values() {
            let (x, y) = self.project_to_2d(&node.position, width, height);
            
            if x < width && y < height {
                let symbol = match node.node_type {
                    NodeType::Gateway => '⚡',
                    NodeType::Tool => '🔧',
                    NodeType::Container => '📦',
                    NodeType::FileSystem => '📁',
                    NodeType::Network => '🌐',
                    NodeType::Process => '⚙',
                    NodeType::Cache => '💾',
                };
                canvas[y][x] = symbol;
            }
        }
        
        // Draw connections
        for node in self.scene.nodes.values() {
            let (x1, y1) = self.project_to_2d(&node.position, width, height);
            
            for conn_id in &node.connections {
                if let Some(target) = self.scene.nodes.get(conn_id) {
                    let (x2, y2) = self.project_to_2d(&target.position, width, height);
                    self.draw_line(&mut canvas, x1, y1, x2, y2, '-');
                }
            }
        }
        
        // Draw active flows
        for flow in &self.scene.flows {
            if flow.status == FlowStatus::Active {
                if let Some(point) = flow.path.last() {
                    let (x, y) = self.project_to_2d(&point.position, width, height);
                    if x < width && y < height {
                        canvas[y][x] = '●';
                    }
                }
            }
        }
        
        // Convert canvas to string
        canvas.iter()
            .map(|row| row.iter().collect::<String>())
            .collect::<Vec<_>>()
            .join("\n")
    }

    /// Generate JSON visualization data
    pub fn export_json(&self) -> String {
        serde_json::to_string_pretty(&self.scene).unwrap_or_default()
    }

    /// Generate SVG visualization
    pub fn export_svg(&self, width: usize, height: usize) -> String {
        let mut svg = format!(
            r#"<svg width="{}" height="{}" xmlns="http://www.w3.org/2000/svg">
"#,
            width, height
        );
        
        // Background
        svg.push_str(&format!(
            r#"  <rect width="{}" height="{}" fill="#1a1a2e"/>
"#,
            width, height
        ));
        
        // Draw connections
        for node in self.scene.nodes.values() {
            let (x1, y1) = self.project_to_2d(&node.position, width, height);
            
            for conn_id in &node.connections {
                if let Some(target) = self.scene.nodes.get(conn_id) {
                    let (x2, y2) = self.project_to_2d(&target.position, width, height);
                    
                    svg.push_str(&format!(
                        r#"  <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#4a4a6a" stroke-width="2" opacity="0.5"/>
"#,
                        x1, y1, x2, y2
                    ));
                }
            }
        }
        
        // Draw nodes
        for node in self.scene.nodes.values() {
            let (x, y) = self.project_to_2d(&node.position, width, height);
            let color = format!("rgb({},{},{})", node.color.r, node.color.g, node.color.b);
            let radius = node.size * 10.0;
            
            svg.push_str(&format!(
                r#"  <circle cx="{}" cy="{}" r="{}" fill="{}" opacity="{}"/>
"#,
                x, y, radius, color, node.color.a
            ));
            
            svg.push_str(&format!(
                r#"  <text x="{}" y="{}" fill="white" font-size="10" text-anchor="middle">{}</text>
"#,
                x, y + radius + 15.0, node.id
            ));
        }
        
        // Draw active flows
        for flow in &self.scene.flows {
            if flow.status == FlowStatus::Active {
                for i in 0..flow.path.len().saturating_sub(1) {
                    let (x1, y1) = self.project_to_2d(&flow.path[i].position, width, height);
                    let (x2, y2) = self.project_to_2d(&flow.path[i + 1].position, width, height);
                    
                    let torsion_color = self.torsion_to_color(flow.path[i].torsion);
                    
                    svg.push_str(&format!(
                        r#"  <line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="3" opacity="0.8"/>
"#,
                        x1, y1, x2, y2, torsion_color
                    ));
                }
            }
        }
        
        svg.push_str("</svg>");
        svg
    }

    /// Recalculate node positions based on layout algorithm
    fn recalculate_layout(&mut self) {
        match self.layout_algorithm {
            LayoutAlgorithm::ForceDirected => self.apply_force_directed_layout(),
            LayoutAlgorithm::Hierarchical => self.apply_hierarchical_layout(),
            LayoutAlgorithm::Circular => self.apply_circular_layout(),
            LayoutAlgorithm::Grid => self.apply_grid_layout(),
        }
    }

    /// Force-directed layout algorithm
    fn apply_force_directed_layout(&mut self) {
        let node_ids: Vec<_> = self.scene.nodes.keys().cloned().collect();
        let iterations = 50;
        let k = 2.0; // Optimal distance
        
        for _ in 0..iterations {
            let mut forces: HashMap<String, Vector3D> = HashMap::new();
            
            // Repulsive forces between all nodes
            for i in 0..node_ids.len() {
                for j in (i + 1)..node_ids.len() {
                    if let (Some(node1), Some(node2)) = (
                        self.scene.nodes.get(&node_ids[i]),
                        self.scene.nodes.get(&node_ids[j])
                    ) {
                        let delta = self.subtract(&node1.position, &node2.position);
                        let distance = self.magnitude(&delta).max(0.1);
                        let force_mag = k * k / distance;
                        let force = self.normalize(&delta, force_mag);
                        
                        *forces.entry(node_ids[i].clone()).or_insert(Vector3D { x: 0.0, y: 0.0, z: 0.0 }) = 
                            self.add(forces.get(&node_ids[i]).unwrap_or(&Vector3D { x: 0.0, y: 0.0, z: 0.0 }), &force);
                        
                        let neg_force = Vector3D { x: -force.x, y: -force.y, z: -force.z };
                        *forces.entry(node_ids[j].clone()).or_insert(Vector3D { x: 0.0, y: 0.0, z: 0.0 }) = 
                            self.add(forces.get(&node_ids[j]).unwrap_or(&Vector3D { x: 0.0, y: 0.0, z: 0.0 }), &neg_force);
                    }
                }
            }
            
            // Apply forces
            for (id, force) in forces {
                if let Some(node) = self.scene.nodes.get_mut(&id) {
                    node.position.x += force.x * 0.01;
                    node.position.y += force.y * 0.01;
                    node.position.z += force.z * 0.01;
                }
            }
        }
    }

    fn apply_hierarchical_layout(&mut self) {
        let mut y = 0.0;
        for node in self.scene.nodes.values_mut() {
            node.position.y = y;
            y += 2.0;
        }
    }

    fn apply_circular_layout(&mut self) {
        let count = self.scene.nodes.len();
        let radius = 5.0;
        
        for (i, node) in self.scene.nodes.values_mut().enumerate() {
            let angle = (i as f32 / count as f32) * 2.0 * std::f32::consts::PI;
            node.position.x = radius * angle.cos();
            node.position.z = radius * angle.sin();
            node.position.y = 0.0;
        }
    }

    fn apply_grid_layout(&mut self) {
        let grid_size = (self.scene.nodes.len() as f32).sqrt().ceil() as usize;
        
        for (i, node) in self.scene.nodes.values_mut().enumerate() {
            let row = i / grid_size;
            let col = i % grid_size;
            node.position.x = col as f32 * 2.0;
            node.position.z = row as f32 * 2.0;
            node.position.y = 0.0;
        }
    }

    fn update_metrics(&mut self) {
        self.scene.metrics_overlay.total_requests += 1;
        self.scene.metrics_overlay.active_flows = 
            self.scene.flows.iter().filter(|f| f.status == FlowStatus::Active).count();
        
        let total_torsion: f32 = self.scene.flows.iter()
            .flat_map(|f| &f.torsion_map)
            .sum();
        let count = self.scene.flows.iter()
            .map(|f| f.torsion_map.len())
            .sum::<usize>() as f32;
        
        self.scene.metrics_overlay.avg_torsion = if count > 0.0 {
            total_torsion / count
        } else {
            0.0
        };
    }

    fn project_to_2d(&self, pos: &Vector3D, width: usize, height: usize) -> (usize, usize) {
        let scale = 20.0;
        let x = ((pos.x * scale + width as f32 / 2.0) as usize).min(width - 1);
        let y = ((pos.z * scale + height as f32 / 2.0) as usize).min(height - 1);
        (x, y)
    }

    fn draw_line(&self, canvas: &mut Vec<Vec<char>>, x1: usize, y1: usize, x2: usize, y2: usize, ch: char) {
        let dx = (x2 as i32 - x1 as i32).abs();
        let dy = (y2 as i32 - y1 as i32).abs();
        let sx = if x1 < x2 { 1 } else { -1 };
        let sy = if y1 < y2 { 1 } else { -1 };
        let mut err = dx - dy;
        let mut x = x1 as i32;
        let mut y = y1 as i32;
        
        loop {
            if x >= 0 && x < canvas[0].len() as i32 && y >= 0 && y < canvas.len() as i32 {
                canvas[y as usize][x as usize] = ch;
            }
            
            if x == x2 as i32 && y == y2 as i32 { break; }
            
            let e2 = 2 * err;
            if e2 > -dy {
                err -= dy;
                x += sx;
            }
            if e2 < dx {
                err += dx;
                y += sy;
            }
        }
    }

    fn torsion_to_color(&self, torsion: f32) -> String {
        if torsion < 0.05 {
            "#00ff00".to_string() // Green - low torsion
        } else if torsion < 0.1 {
            "#ffff00".to_string() // Yellow - medium torsion
        } else {
            "#ff0000".to_string() // Red - high torsion
        }
    }

    // Vector math helpers
    fn subtract(&self, a: &Vector3D, b: &Vector3D) -> Vector3D {
        Vector3D { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z }
    }

    fn add(&self, a: &Vector3D, b: &Vector3D) -> Vector3D {
        Vector3D { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z }
    }

    fn magnitude(&self, v: &Vector3D) -> f32 {
        (v.x * v.x + v.y * v.y + v.z * v.z).sqrt()
    }

    fn normalize(&self, v: &Vector3D, mag: f32) -> Vector3D {
        let len = self.magnitude(v);
        if len > 0.0 {
            Vector3D {
                x: (v.x / len) * mag,
                y: (v.y / len) * mag,
                z: (v.z / len) * mag,
            }
        } else {
            Vector3D { x: 0.0, y: 0.0, z: 0.0 }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_holographic_debugger_creation() {
        let debugger = HolographicDebugger::new();
        assert_eq!(debugger.scene.nodes.len(), 0);
    }

    #[test]
    fn test_add_node() {
        let mut debugger = HolographicDebugger::new();
        let node = HolographicNode {
            id: "gateway-1".to_string(),
            position: Vector3D { x: 0.0, y: 0.0, z: 0.0 },
            node_type: NodeType::Gateway,
            size: 1.0,
            color: Color { r: 255, g: 255, b: 0, a: 1.0 },
            activity_level: 0.5,
            connections: vec![],
        };
        
        debugger.add_node(node);
        assert_eq!(debugger.scene.nodes.len(), 1);
    }

    #[test]
    fn test_ascii_render() {
        let debugger = HolographicDebugger::new();
        let ascii = debugger.render_ascii(80, 24);
        assert!(!ascii.is_empty());
    }
}
