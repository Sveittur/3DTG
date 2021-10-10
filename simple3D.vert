attribute vec3 a_normal;
attribute vec3 a_position;


uniform mat4 u_model_matrix;
uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;


//uniform vec4 u_color;
uniform vec4 u_eye_position;

uniform vec4 u_light_position;
uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;

uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;

varying vec4 v_color;  //Leave the varying variables alone to begin with

void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x,a_normal.y,a_normal.z,0.0);

	position = u_model_matrix * position;
	normal = normalize(u_model_matrix * normal);

	// Global coordinates

	vec4 s = normalize(u_light_position - position);
	float lambert = max(dot(normal,s),0);
	v_color = u_light_diffuse * u_mat_diffuse * lambert;

	vec4 v = normalize(u_eye_position - position);
	vec4 h = normalize(s + v);
	float phong = max(dot(normal,h),0);

	v_color = u_light_diffuse * u_mat_diffuse * lambert
			  + u_light_specular * u_mat_specular * pow(phong,u_mat_shininess); 
	//float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	//float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	//v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####

	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
	
	position = (u_view_matrix * position);
	//eye coordinates
	position = u_projection_matrix * position;
	// clipping coordinates

	gl_Position = position;
}