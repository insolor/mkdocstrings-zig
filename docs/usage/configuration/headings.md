# Headings options

[](){ #option-heading }
## `heading`

- **:octicons-package-24: Type [`str`][] :material-equal: `""`{ title="default value" }**

A custom string to use as the heading of the root object (i.e. the object specified directly after the identifier `:::`). This will override the default heading generated by the plugin. See also the [`toc_label` option][option-toc_label].

WARNING: **Not advised to be used as a global configuration option.** This option is not advised to be used as a global configuration option, as it will override the default heading for all objects. It is recommended to use it only in specific cases where you want to override the heading for a specific object.

```md title="in docs/some_page.md (local configuration)"
::: path.to.module
    options:
      heading: "My fancy module"
```

[](){ #option-heading_level }
## `heading_level`

- **:octicons-package-24: Type [`int`][] :material-equal: `2`{ title="default value" }**

The initial heading level to use.

When injecting documentation for an object,
the object itself and its members are rendered.
For each layer of objects, we increase the heading level by 1.

The initial heading level will be used for the first layer.
If you set it to 3, then headings will start with `<h3>`.

```yaml title="in mkdocs.yml (global configuration)"
plugins:
- mkdocstrings:
    handlers:
      zig:
        options:
          heading_level: 2
```

```md title="or in docs/some_page.md (local configuration)"
::: path.to.module
    options:
      heading_level: 3
```

/// admonition | Preview
    type: preview

//// tab | With level 3 and root heading
<h3><code>module</code> (3)</h3>
<p>Docstring of the module.</p>
<h4><code>ClassA</code> (4)</h4>
<p>Docstring of class A.</p>
<h4><code>ClassB</code> (4)</h4>
<p>Docstring of class B.</p>
<h5><code>method_1</code> (5)</h5>
<p>Docstring of the method.</p>
////

//// tab | With level 3, without root heading
<p>Docstring of the module.</p>
<h3><code>ClassA</code> (3)</h3>
<p>Docstring of class A.</p>
<h3><code>ClassB</code> (3)</h3>
<p>Docstring of class B.</p>
<h4><code>method_1</code> (4)</h4>
<p>Docstring of the method.</p>
////
///


[](){ #option-show_symbol_type_heading }
## `show_symbol_type_heading`

- **:octicons-package-24: Type [`bool`][] :material-equal: `False`{ title="default value" }**

Show the symbol type in headings.

This option will prefix headings with
<code class="doc-symbol doc-symbol-attribute"></code>,
<code class="doc-symbol doc-symbol-function"></code>,
<code class="doc-symbol doc-symbol-method"></code>,
<code class="doc-symbol doc-symbol-class"></code> or
<code class="doc-symbol doc-symbol-module"></code> types.
See also [`show_symbol_type_toc`][show_symbol_type_toc].

To customize symbols, see [Customizing symbol types](../customization.md/#symbol-types).

```yaml title="in mkdocs.yml (global configuration)"
plugins:
- mkdocstrings:
    handlers:
      zig:
        options:
          show_symbol_type_heading: true
```

```md title="or in docs/some_page.md (local configuration)"
::: package.module
    options:
      show_symbol_type_heading: false
```

/// admonition | Preview
    type: preview

//// tab | With symbol type in headings
<h1><code class="doc-symbol doc-symbol-module"></code> <code>module</code></h1>
<p>Docstring of the module.</p>
<h2><code class="doc-symbol doc-symbol-attribute"></code> <code>attribute</code></h2>
<p>Docstring of the module attribute.</p>
<h2><code class="doc-symbol doc-symbol-function"></code> <code>function</code></h2>
<p>Docstring of the function.</p>
<h2><code class="doc-symbol doc-symbol-class"></code> <code>Class</code></h2>
<p>Docstring of the class.</p>
<h3><code class="doc-symbol doc-symbol-method"></code> <code>method</code></h3>
<p>Docstring of the method.</p>
////

//// tab | Without symbol type in headings
<h1><code>module</code></h1>
<p>Docstring of the module.</p>
<h2><code>attribute</code></h2>
<p>Docstring of the module attribute.</p>
<h2><code>function</code></h2>
<p>Docstring of the function.</p>
<h2><code>Class</code></h2>
<p>Docstring of the class.</p>
<h3><code>method</code></h3>
<p>Docstring of the method.</p>
////
///

[](){ #option-show_symbol_type_toc }
## `show_symbol_type_toc`

- **:octicons-package-24: Type [`bool`][] :material-equal: `False`{ title="default value" }**

Show the symbol type in the Table of Contents.

This option will prefix items in the ToC with
<code class="doc-symbol doc-symbol-attribute"></code>,
<code class="doc-symbol doc-symbol-function"></code>,
<code class="doc-symbol doc-symbol-method"></code>,
<code class="doc-symbol doc-symbol-class"></code> or
<code class="doc-symbol doc-symbol-module"></code> types.
See also [`show_symbol_type_heading`][show_symbol_type_heading].

To customize symbols, see [Customizing symbol types](../customization.md/#symbol-types).

```yaml title="in mkdocs.yml (global configuration)"
plugins:
- mkdocstrings:
    handlers:
      zig:
        options:
          show_symbol_type_toc: true
```

```md title="or in docs/some_page.md (local configuration)"
::: package.module
    options:
      show_symbol_type_toc: false
```

/// admonition | Preview
    type: preview

//// tab | With symbol type in ToC
<ul style="list-style: none;">
  <li><code class="doc-symbol doc-symbol-module"></code> module</li>
  <li><code class="doc-symbol doc-symbol-attribute"></code> attribute</li>
  <li><code class="doc-symbol doc-symbol-function"></code> function</li>
  <li><code class="doc-symbol doc-symbol-class"></code> Class
    <ul style="list-style: none;">
      <li><code class="doc-symbol doc-symbol-method"></code> method</li>
    </ul>
  </li>
</ul>
////

//// tab | Without symbol type in ToC
<ul style="list-style: none;">
  <li>module</li>
  <li>attribute</li>
  <li>function</li>
  <li>Class
    <ul style="list-style: none;">
      <li>method</li>
    </ul>
  </li>
</ul>
////
///

[](){ #option-toc_label }
## `toc_label`

- **:octicons-package-24: Type [`str`][] :material-equal: `""`{ title="default value" }**

A custom string to use as the label in the Table of Contents for the root object (i.e. the one specified directly after the identifier `:::`). This will override the default label generated by the plugin. See also the [`heading` option][option-heading].

WARNING: **Not advised to be used as a global configuration option.** This option is not advised to be used as a global configuration option, as it will override the default label for all objects. It is recommended to use it only in specific cases where you want to override the label for a specific object.

NOTE: **Use with/without `heading`.** If you use this option without specifying a custom `heading`, the default heading will be used in the page, but the label in the Table of Contents will be the one you specified. By providing both an option for `heading` and `toc_label`, we leave the customization entirely up to you.

```md title="in docs/some_page.md (local configuration)"
::: path.to.module
    options:
      heading: "My fancy module"
      toc_label: "My fancy module"
```
