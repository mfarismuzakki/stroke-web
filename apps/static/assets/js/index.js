class Index 
{
    init()
    {
        let myChart = null;
        this.pushData(myChart);
        this.onChangeDataype();
    }

    onChangeDataype()
    {
        $("#dropdown").change(function() 
        {
            let data_type = $('option:selected', this).val();
            
            if(data_type == '1')
            {
                $('#klinik-container').hide();
                $('#lab-container').hide();
            }else if(data_type == '2')
            {
                $('#klinik-container').show();
                $('#lab-container').hide();
            }else{
                $('#klinik-container').show();
                $('#lab-container').show();
            }
        })
    }

    pushData(myChart)
    {        
        $("#btn-submit").click(function() 
        {
            const url = '/apis/dashboard';
            let that = this;
            // Mendapatkan nilai dari elemen-elemen formulir menggunakan jQuery
            const dropdownValue = $('#dropdown').val();
            const fileInput = $('#file')[0].files;
            const awitan = $('#awitan').val();
            const usia = $('#usia').val();
            const tensiAtas = $('#tensi_atas').val();
            const tensiBawah = $('#tensi_bawah').val();
            const pt = $('#pt').val();
            const aptt = $('#aptt').val();
            const fibrinogen = $('#fibrinogen').val();
            const gds = $('#gds').val();
            
            // Membuat objek FormData dan menambahkan nilai ke dalamnya
            const formData = new FormData();
            formData.append('dropdown', dropdownValue);
            // formData.append('file', fileInput);
            formData.append('awitan', awitan);
            formData.append('usia', usia);
            formData.append('tensi_atas', tensiAtas);
            formData.append('tensi_bawah', tensiBawah);
            formData.append('pt', pt);
            formData.append('aptt', aptt);
            formData.append('fibrinogen', fibrinogen);
            formData.append('gds', gds);

            // Mengecek apakah ada file yang dipilih
            if (fileInput.length > 0) {
                // Menambahkan setiap file ke FormData
                for (let i = 0; i < fileInput.length; i++) {
                    formData.append('files', fileInput[i]);
                }            
            }
            
            // Melakukan permintaan ke API menggunakan jQuery.ajax()
            let csrf = $('input[name="csrfmiddlewaretoken"]').val(); 
            
            $.ajax({
                url: url,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrf
                },
                data: formData,
                processData: false,
                contentType: false,
                beforeSend: function () {
                    $('#loader').removeClass('display-none');
                },
                success: function(data) {
                    $('#loader').addClass('display-none');
                    $('#modal-xl').modal('show');
                    let result = data['result'];
                    let result_proba = data['result_proba'][0];
                    let html_result = '';

                    if (result == 'signifikan') {
                        html_result = `
                            <div class="alert alert-primary" role="alert">
                                <center>Signifikan</center>
                            </div>
                        `;
                    } else {
                        html_result = `
                            <div class="alert alert-danger" role="alert">
                                <center>Tidak Signifikan</center>
                            </div>
                        `;
                    }
            
                    $('#alert-result').html(html_result);
            
                    // Cek apakah myChart sudah ada
                    if (myChart && myChart.destroy) {
                        myChart.destroy();
                    } 

                    // Jika belum ada, buat chart baru
                    const ctx = document.getElementById('myChart');
                    myChart = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: ['signifikan', 'tidak signifikan'],
                            datasets: [{
                                label: 'Persentase',
                                data: [result_proba[0], result_proba[1]],
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
                            },
                        }
                    });

                    // write the images
                    var imageContainer = $('#image-container');
                    imageContainer.html(`
                        <div class="image-row">
                            <h2>Axial</h2>
                            <img class="img-fluid" src="data:image/png;base64,${data['axial_base64']}" alt="Axial Image 1">
                        </div>
                        <div class="image-row">
                            <h2>Coronal</h2>
                            <img class="img-fluid" src="data:image/png;base64,${data['coronal_base64']}" alt="Coronal Image 2">
                        </div>
                        <div class="image-row">
                            <h2>Sagittal</h2>
                            <img class="img-fluid" src="data:image/png;base64,${data['sagittal_base64']}" alt="Sagittal Image 3"">
                        </div>
                    `);
                },
                error: function(error) {
                    console.log(error.responseText)
                    alert('Error: ' +  error.statusText);
                },
                complete: function(){
                    $('#loader').addClass('display-none');
                }
            });
        })
    }
}
    
new Index().init()