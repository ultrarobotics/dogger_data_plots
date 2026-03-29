import numpy as np

cfg = [
    {
        "env_name": "dogger_env_walking_flat",
        "model_path": "results/dogger_env_walking_flat/20240928_104310/policies/highest_policy",  #'results/dogger_env_walking_flat/20240829_151717/policies/highest_policy',
        "command": np.array(
            [[0.0, -0.5, 0.0], [0.0, -0.0, 0.0]]
        ),  # np.array([0.0, -0.8, 0.0]), # None
        "scaling_factor_min": 0.7,  # 0.7 min
        "scaling_factor_max": 1.3,  # 1.3 max
        "spring_offset_length_range": (
            0.0,
            0.01,
        ),  # range of the offset length of the spring in m. (0, 0.01)
        "spring_wheel_diameter_range": (
            0.0,
            0.05,
        ),  # range of the wheel diameter in m. (0, 0.05)
        "scene_path": None,
        "episode_length": 6000,
        "action_repeat": 1,
        "additional_mass": 0.0,
        "num_envs": 16384,
        "num_runs": 2,
        "seed": 1,
        "normalize_observations": True,
        "compare_policies": ["20240424_123212", "20240424_150620"],
        "demo": {
            "gamepad": {
                "offset": 128,
                "max_value": 128,
                "x_factor": 0.6,
                "y_low_factor": 0.6,
                "y_high_factor": 0.8,
                "z_factor": 1.0,
            },
            "scene_path": "dogger_model/scene_mjx.xml",
        },
        "plotting": {
            "metric": "metric_power_dist",
            "optimize_for": "minimize",  # 'minimize' or 'maximize'
        },
        "hyperparameters": {
            "network": {
                "policy_hidden_layer_sizes": (128, 128, 128, 128),
            },
        },
    },
    {
        "env_name": "dogger_env_pronking",
        "model_path": "results/dogger_env_pronking/20240731_115320/policies/highest_policy",
        "command": np.array([0.0, -0.5, 0.0]),  # np.array([0.0, -0.8, 0.0]), # None
        "scaling_factor_min": 0.7,  # 0.7 min
        "scaling_factor_max": 1.3,  # 1.3 max
        "spring_offset_length_range": (
            0.0,
            0.01,
        ),  # range of the offset length of the spring in m. (0, 0.01)
        "spring_wheel_diameter_range": (
            0.0,
            0.05,
        ),  # range of the wheel diameter in m. (0, 0.05)
        "scene_path": None,
        "episode_length": 2500,
        "action_repeat": 1,
        "additional_mass": 0.0,
        "num_envs": 16384,
        "num_runs": 1,  # ,
        "seed": 0,
        "normalize_observations": True,
        "compare_policies": ["20240424_123212", "20240424_150620"],
        "demo": {
            "gamepad": {
                "offset": 128,
                "max_value": 128,
                "x_factor": 0.8,
                "y_low_factor": 0.8,
                "y_high_factor": 1.2,
                "z_factor": 1.2,
            },
            "scene_path": "dogger_model/scene_mjx.xml",
        },
        "plotting": {
            "metric": "metric_air_time",
            "optimize_for": "maximize",  # 'minimize' or 'maximize'
        },
        "hyperparameters": {
            "network": {
                "policy_hidden_layer_sizes": (256, 256, 256, 256),
            },
        },
    },
    {
        "env_name": "dogger_env_walking_rough",
        "model_path": "results/dogger_env_walking_flat/20240928_104310/policies/highest_policy",
        "command": None,  # np.array([-0.5, -0.0, 0.0]), #, #,
        "scaling_factor_min": 0.7,  # 0.7 min
        "scaling_factor_max": 1.3,  # 1.3 max
        "spring_offset_length_range": (
            0.0,
            0.01,
        ),  # range of the offset length of the spring in m. (0, 0.01)
        "spring_wheel_diameter_range": (
            0.0,
            0.05,
        ),  # range of the wheel diameter in m. (0, 0.05)
        "scene_path": "dogger_model/scene_mjx_payload.xml",  # dogger_model/scene_rough_eval.xml
        "additional_mass": 0.0,
        "episode_length": 15000,
        "action_repeat": 1,
        "num_envs": 16384,
        "num_runs": 1,
        "seed": 0,
        "normalize_observations": True,
        "compare_policies": ["20240424_123212", "20240424_150620"],
        "demo": {
            "gamepad": {
                "offset": 128,
                "max_value": 128,
                "x_factor": 0.6,
                "y_low_factor": 0.6,
                "y_high_factor": 0.8,
                "z_factor": 0.6,
            },
            "scene_path": "dogger_model/scene_mjx_payload.xml",
        },
        "plotting": {
            "metric": "metric_power_dist",
            "optimize_for": "minimize",  # 'minimize' or 'maximize'
        },
        "hyperparameters": {
            "network": {
                "policy_hidden_layer_sizes": (128, 128, 128, 128),
            },
        },
    },
    {
        "env_name": "dogger_env_walking_rough",
        "model_path": "results/dogger_env_walking_flat/20240928_104310/policies/highest_policy",
        "command": np.array(
            [
                [0.0, -0.35, 0.0],
                [0.25, 0.0, 0.0],
                [-0.2, 0.2, 0.0],
                [0.0, -0.2, -0.3],
                [0.0, 0.15, 0.3],
                [0.1, 0.2, -0.2],
                [-0.1, -0.2, 0.1],
                [0.0, -0.2, 0.0],
                [0.0, -0.2, 0.4],
                [0.0, 0.2, -0.2],
                [0.0, -0.2, 0.1],
                [0.2, 0.0, 0.0],
                [0.0, 0.0, -0.5],
                [-0.1, 0.2, -0.1],
            ]
        ),  # np.array([-0.5, -0.0, 0.0]), #, #,
        "scaling_factor_min": 0.7,  # 0.7 min
        "scaling_factor_max": 1.3,  # 1.3 max
        "spring_offset_length_range": (
            0.0,
            0.01,
        ),  # range of the offset length of the spring in m. (0, 0.01)
        "spring_wheel_diameter_range": (
            0.0,
            0.05,
        ),  # range of the wheel diameter in m. (0, 0.05)
        "scene_path": "dogger_model/scene_mjx_payload.xml",  # dogger_model/scene_rough_eval.xml
        "additional_mass": 0.0,
        "episode_length": 6000,
        "action_repeat": 1,
        "num_envs": 16384,
        "num_runs": 1,
        "seed": 0,
        "normalize_observations": True,
        "compare_policies": ["20240424_123212", "20240424_150620"],
        "demo": {
            "gamepad": {
                "offset": 128,
                "max_value": 128,
                "x_factor": 0.6,
                "y_low_factor": 0.6,
                "y_high_factor": 0.8,
                "z_factor": 0.6,
            },
            "scene_path": "dogger_model/scene_mjx_payload.xml",
        },
        "plotting": {
            "metric": "metric_power_dist",
            "optimize_for": "minimize",  # 'minimize' or 'maximize'
        },
        "hyperparameters": {
            "network": {
                "policy_hidden_layer_sizes": (128, 128, 128, 128),
            },
        },
    },
]
