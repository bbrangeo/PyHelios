from pyhelios import Context
from pyhelios.types import *

context = Context()

center = vec3(2, 3, 4)
size = vec2(1, 1)
color = RGBcolor(0.25, 0.25, 0.25)

patch_uuid = context.addPatch(
    center=center,
    size=size,
    color=color
)

print(f'patch_uuid: {patch_uuid}')

print(f'context.getPrimitiveType(patch_uuid): {context.getPrimitiveType(patch_uuid)}')

print(f'context.getPrimitiveArea(patch_uuid): {context.getPrimitiveArea(patch_uuid)}')

print(f'context.getPrimitiveNormal(patch_uuid): {context.getPrimitiveNormal(patch_uuid)}')

print(f'context.getPrimitiveVertices(patch_uuid): {context.getPrimitiveVertices(patch_uuid)}')

print(f'context.getPrimitiveColor(patch_uuid): {context.getPrimitiveColor(patch_uuid)}')


