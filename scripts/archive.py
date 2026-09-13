# TEMPLATES = {
#     "VDST_SRC0_VSRC1_F16": VDST_SRC0_VSRC1_F16,
#     "VDST_SRC0_VSRC1_F32": VDST_SRC0_VSRC1_F32,
#     "VDST_SRC0_VSRC1_F64": VDST_SRC0_VSRC1_F64,
#     "VDST_SRC0_VSRC1_LITERAL_F16": VDST_SRC0_VSRC1_LITERAL_F16,
#     "VDST_SRC0_VSRC1_LITERAL_F32": VDST_SRC0_VSRC1_LITERAL_F32,
#     "VDST_SRC0_LITERAL_VSRC1_F16": VDST_SRC0_LITERAL_VSRC1_F16,
#     "VDST_SRC0_LITERAL_VSRC1_F32": VDST_SRC0_LITERAL_VSRC1_F32,
#     "VDST_SRC0_VSRC1_B32": VDST_SRC0_VSRC1_B32,
#     "VDST_SRC0_VSRC1_B64": VDST_SRC0_VSRC1_B64,
#     "VDST_SRC0_VSRC1_U32": VDST_SRC0_VSRC1_U32,
#     "VDST_SRC0_VSRC1_I32": VDST_SRC0_VSRC1_I32,
#     "VDST_SRC0_VSRC1_CARRY_U32": VDST_SRC0_VSRC1_CARRY_U32,
#     "VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32": VDST_SDST_SRC0_VSRC1_VCC_VECTOR_U32,
#     "VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32": VDST_SDST_SRC0_VSRC1_VCC_CARRY_U32
# }

INSTRUCTION_GROUPS = {
    "VDST_SRC0_VSRC1_F16": {
        "v_add_f16",
        "v_ldexp_f16",
        "v_max_num_f16",
        "v_min_num_f16",
        "v_mul_f16",
        "v_subrev_f16",
        "v_sub_f16",
    },

    "VDST_SRC0_VSRC1_F32": {
        "v_add_f32",
        "v_cvt_pk_rtz_f16_f32",
        "v_max_num_f32",
        "v_min_num_f32",
        "v_mul_dx9_zero_f32",
        "v_mul_f32",
        "v_subrev_f32",
        "v_sub_f32",
    },

    "VDST_SRC0_VSRC1_F64": {
        "v_max_num_f64",
        "v_min_num_f64",
        "v_mul_f64",
    },

    "VDST_SRC0_VSRC1_B32": {
        "v_and_b32",
        "v_lshlrev_b32",
        "v_or_b32",
    },

    "VDST_SRC0_VSRC1_B64": {
        "v_lshlrev_b64",
    },

    "VDST_SRC0_VSRC1_U32": {
        "v_add_nc_u32",
        "v_max_u32",
        "v_min_u32",
        "v_subrev_nc_u32",
        "v_sub_nc_u32"
    },

    "VDST_SRC0_VSRC1_CARRY_U32": {
        "v_add_co_ci_u32",
        "v_subrev_co_ci_u32",
        "v_sub_co_ci_u32"
    },

    "VDST_SRC0_VSRC1_I32": {
        "v_ashrrev_i32",
        "v_max_i32",
        "v_min_i32",
    },

    "VDST_SRC0_VSRC1_LITERAL_F16": {
        "v_fmaak_f16"
    },

    "VDST_SRC0_VSRC1_LITERAL_F32": {
        "todo"
    },

    "VDST_SRC0_LITERAL_VSRC1_F16": {
        "v_fmamk_f16"
    },

    "VDST_SRC0_LITERAL_VSRC1_F32": {
        "v_fmamk_f32"
    },

    "VDST_SRC0_VSRC1_VCC_B32": {
        "v_cndmask_b32",
        "v_xnor_b32",
        "v_xor_b32",
    },

    "VDST_SDST_SRC0_VSRC1_VCC_U32": {
        "todo"
    },
}