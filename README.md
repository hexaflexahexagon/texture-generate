# texture-generate
automatically generates pleasant looking custom grid textures for use in team fortress 2 mapping. 

needs vtflib installed (https://github.com/NeilJed/VTFLib)

to use edit the script to correct any file paths that need to be set. then simply run the script and select which type of texture you would like to generate. the options for soldity are:
- opaque, no transparency in the texture.
- glass, meaning the texture is transparent (`$transparent 1` is also added to the vmt)

the options for added noise are:
- perlin, a nicer and blobbier visually interesting texture
- gaussian, a small static-y noise that is much less intrusive. helps prevent the texture from being "flat" and hurting gameplay
- no noise, meaning the middle section will be a solid color. not recommended but more power to you

examples of all of the above are located in the `examples` folder.
